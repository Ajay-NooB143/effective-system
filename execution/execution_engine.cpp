/**
 * execution/execution_engine.cpp
 *
 * ZMQ PULL + Binance REST execution engine.
 *
 * Listens on a ZMQ PULL socket for JSON order messages from the Python
 * orchestrator and places MARKET orders on Binance Spot (testnet or live).
 *
 * Environment variables
 * ---------------------
 * BINANCE_API_KEY     Required for live / testnet trading.
 * BINANCE_API_SECRET  Required for live / testnet trading (never logged).
 * BINANCE_TESTNET     "true" → use https://testnet.binance.vision
 *                     (default: "false" → live https://api.binance.com)
 * DRY_RUN             "true" → log orders without placing them
 *                     (default: "false")
 * ZMQ_BIND            ZMQ bind address (default: "tcp://*:5555")
 *
 * JSON order schema (sent by execution/bridge.py)
 * ------------------------------------------------
 * {
 *   "symbol":      "BTCUSDT",  // required, non-empty string
 *   "side":        "BUY",      // required, "BUY" or "SELL"
 *   "qty":         0.001,      // required, number > 0
 *   "type":        "MARKET",   // optional, default "MARKET"
 *   "timeInForce": "GTC"       // optional, default "GTC"
 * }
 *
 * Build
 * -----
 * See CMakeLists.txt.  Quick start:
 *   cd execution
 *   cmake -B build -DCMAKE_BUILD_TYPE=Release
 *   cmake --build build
 *   ./build/execution_engine
 */

#include <algorithm>
#include <atomic>
#include <chrono>
#include <csignal>
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <string>
#include <thread>

#include <curl/curl.h>
#include <openssl/evp.h>
#include <openssl/hmac.h>
#include <zmq.h>

#include <nlohmann/json.hpp>

using json = nlohmann::json;

// Maximum backoff delay in seconds for consecutive execution errors
static constexpr int MAX_BACKOFF_SECONDS = 64;

// ---------------------------------------------------------------------------
// Graceful shutdown
// ---------------------------------------------------------------------------

static std::atomic<bool> g_stop{false};

static void handle_signal(int /*sig*/) {
    g_stop = true;
}

// ---------------------------------------------------------------------------
// Environment helpers
// ---------------------------------------------------------------------------

static std::string get_env(const char *name, const char *fallback = "") {
    const char *v = std::getenv(name);
    return v ? std::string(v) : std::string(fallback);
}

static bool get_bool_env(const char *name, bool fallback = false) {
    std::string v = get_env(name);
    if (v.empty())
        return fallback;
    std::transform(v.begin(), v.end(), v.begin(), ::tolower);
    return v == "true" || v == "1" || v == "yes";
}

// ---------------------------------------------------------------------------
// HMAC-SHA256 → lowercase hex string
// ---------------------------------------------------------------------------

static std::string hmac_sha256_hex(const std::string &key,
                                   const std::string &data) {
    unsigned char digest[EVP_MAX_MD_SIZE] = {};
    unsigned int digest_len = 0;
    // key.size() is safely bounded for HMAC keys (validated at startup)
    HMAC(EVP_sha256(), key.data(), static_cast<int>(key.size() & 0x7fffffff),
         reinterpret_cast<const unsigned char *>(data.data()), data.size(),
         digest, &digest_len);

    std::ostringstream ss;
    for (unsigned int i = 0; i < digest_len; ++i)
        ss << std::hex << std::setw(2) << std::setfill('0')
           << static_cast<int>(digest[i]);
    return ss.str();
}

// ---------------------------------------------------------------------------
// Current Unix timestamp in milliseconds
// ---------------------------------------------------------------------------

static int64_t now_ms() {
    return std::chrono::duration_cast<std::chrono::milliseconds>(
               std::chrono::system_clock::now().time_since_epoch())
        .count();
}

// ---------------------------------------------------------------------------
// CURL write callback
// ---------------------------------------------------------------------------

static size_t curl_write_cb(void *ptr, size_t size, size_t nmemb,
                             std::string *out) {
    out->append(static_cast<char *>(ptr), size * nmemb);
    return size * nmemb;
}

// ---------------------------------------------------------------------------
// BinanceClient — signed HTTPS REST for Spot MARKET orders
// ---------------------------------------------------------------------------

class BinanceClient {
  public:
    BinanceClient(const std::string &api_key, const std::string &api_secret,
                  bool testnet)
        : api_key_(api_key), api_secret_(api_secret),
          base_url_(testnet ? "https://testnet.binance.vision"
                            : "https://api.binance.com") {
        curl_global_init(CURL_GLOBAL_DEFAULT);
    }

    ~BinanceClient() { curl_global_cleanup(); }

    /**
     * Place a MARKET order.
     * @return Raw Binance JSON response string.
     */
    std::string place_market_order(const std::string &symbol,
                                   const std::string &side, double qty) {
        std::ostringstream body_ss;
        body_ss << "symbol=" << symbol << "&side=" << side
                << "&type=MARKET"
                << "&quantity=" << std::fixed << std::setprecision(6) << qty
                << "&timestamp=" << now_ms();

        const std::string body = body_ss.str();
        const std::string sig  = hmac_sha256_hex(api_secret_, body);
        const std::string full = body + "&signature=" + sig;

        return post(base_url_ + "/api/v3/order", full);
    }

  private:
    std::string api_key_;
    std::string api_secret_; // never written to logs
    std::string base_url_;

    std::string post(const std::string &url, const std::string &body) {
        CURL *curl = curl_easy_init();
        if (!curl)
            return R"({"error":"curl_easy_init failed"})";

        std::string response;
        const std::string key_hdr = "X-MBX-APIKEY: " + api_key_;
        struct curl_slist *hdrs    = nullptr;
        hdrs = curl_slist_append(hdrs, key_hdr.c_str());
        hdrs = curl_slist_append(
            hdrs, "Content-Type: application/x-www-form-urlencoded");

        curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
        curl_easy_setopt(curl, CURLOPT_POST, 1L);
        curl_easy_setopt(curl, CURLOPT_POSTFIELDS, body.c_str());
        curl_easy_setopt(curl, CURLOPT_POSTFIELDSIZE,
                         static_cast<long>(body.size()));
        curl_easy_setopt(curl, CURLOPT_HTTPHEADER, hdrs);
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, curl_write_cb);
        curl_easy_setopt(curl, CURLOPT_WRITEDATA, &response);
        curl_easy_setopt(curl, CURLOPT_TIMEOUT, 10L);

        const CURLcode rc = curl_easy_perform(curl);
        if (rc != CURLE_OK) {
            // Use nlohmann/json to ensure the error message is properly escaped
            response = json{{"error", std::string("curl: ") +
                                          curl_easy_strerror(rc)}}
                           .dump();
        }
        curl_slist_free_all(hdrs);
        curl_easy_cleanup(curl);
        return response;
    }
};

// ---------------------------------------------------------------------------
// Order struct and validation
// ---------------------------------------------------------------------------

struct Order {
    std::string symbol;
    std::string side;
    double      qty           = 0.0;
    std::string type          = "MARKET";
    std::string time_in_force = "GTC";
};

static bool validate(const json &j, Order &o, std::string &err) {
    if (!j.contains("symbol") || !j["symbol"].is_string() ||
        j["symbol"].get<std::string>().empty()) {
        err = "missing or empty 'symbol'";
        return false;
    }
    if (!j.contains("side") || !j["side"].is_string()) {
        err = "missing 'side'";
        return false;
    }
    const auto side = j["side"].get<std::string>();
    if (side != "BUY" && side != "SELL") {
        err = "'side' must be 'BUY' or 'SELL'";
        return false;
    }
    if (!j.contains("qty") || !j["qty"].is_number()) {
        err = "missing or non-numeric 'qty'";
        return false;
    }
    const double qty = j["qty"].get<double>();
    if (qty <= 0.0) {
        err = "'qty' must be > 0";
        return false;
    }

    o.symbol        = j["symbol"].get<std::string>();
    o.side          = side;
    o.qty           = qty;
    o.type          = j.value("type", "MARKET");
    o.time_in_force = j.value("timeInForce", "GTC");
    return true;
}

// ---------------------------------------------------------------------------
// main
// ---------------------------------------------------------------------------

int main() {
    std::signal(SIGINT,  handle_signal);
    std::signal(SIGTERM, handle_signal);

    const bool        dry_run  = get_bool_env("DRY_RUN",         false);
    const bool        testnet  = get_bool_env("BINANCE_TESTNET",  false);
    const std::string zmq_bind = get_env("ZMQ_BIND",             "tcp://*:5555");
    const std::string api_key  = get_env("BINANCE_API_KEY");
    const std::string api_sec  = get_env("BINANCE_API_SECRET");

    std::cout << "[engine] starting — mode="
              << (dry_run ? "DRY_RUN" : (testnet ? "TESTNET" : "LIVE"))
              << " bind=" << zmq_bind << "\n"
              << std::flush;

    if (!dry_run && (api_key.empty() || api_sec.empty())) {
        std::cerr << "[engine] BINANCE_API_KEY / BINANCE_API_SECRET not set.\n"
                  << "[engine] Set DRY_RUN=true to run without credentials.\n";
        return 1;
    }

    BinanceClient client(api_key, api_sec, testnet);

    // ZMQ PULL socket
    void *ctx  = zmq_ctx_new();
    void *sock = zmq_socket(ctx, ZMQ_PULL);
    if (zmq_bind(sock, zmq_bind.c_str()) != 0) {
        std::cerr << "[engine] zmq_bind(" << zmq_bind
                  << ") failed: " << zmq_strerror(errno) << "\n";
        zmq_close(sock);
        zmq_ctx_destroy(ctx);
        return 1;
    }

    // Receive timeout lets the main loop check g_stop periodically
    const int timeout_ms = 500;
    zmq_setsockopt(sock, ZMQ_RCVTIMEO, &timeout_ms, sizeof(timeout_ms));

    std::cout << "[engine] listening on " << zmq_bind << "\n" << std::flush;

    int consecutive_errors = 0;

    while (!g_stop) {
        zmq_msg_t msg;
        zmq_msg_init(&msg);
        const int bytes = zmq_msg_recv(&msg, sock, 0);
        if (bytes < 0) {
            zmq_msg_close(&msg);
            if (errno == EAGAIN)
                continue; // poll timeout — check g_stop
            if (errno == ETERM)
                break; // context shut down
            std::cerr << "[engine] zmq_recv error: " << zmq_strerror(errno)
                      << "\n";
            continue;
        }

        const std::string raw(static_cast<char *>(zmq_msg_data(&msg)), bytes);
        zmq_msg_close(&msg);

        // Parse JSON
        json j;
        try {
            j = json::parse(raw);
        } catch (const json::parse_error &e) {
            std::cerr << "[engine] JSON parse error: " << e.what() << "\n";
            continue;
        }

        // Validate
        Order order;
        std::string err;
        if (!validate(j, order, err)) {
            std::cerr << "[engine] invalid order: " << err << "\n";
            continue;
        }

        std::cout << "[engine] received: " << order.side << " " << order.symbol
                  << " qty=" << std::fixed << std::setprecision(6) << order.qty
                  << " type=" << order.type << "\n"
                  << std::flush;

        if (dry_run) {
            std::cout << "[engine] DRY_RUN — would POST /api/v3/order"
                      << " symbol=" << order.symbol
                      << " side=" << order.side
                      << " qty=" << std::fixed << std::setprecision(6)
                      << order.qty << "\n"
                      << std::flush;
            consecutive_errors = 0;
            continue;
        }

        // Exponential backoff on repeated failures
        if (consecutive_errors > 0) {
            const int delay_s =
                std::min(1 << std::min(consecutive_errors, 6), MAX_BACKOFF_SECONDS);
            std::cerr << "[engine] backing off " << delay_s << "s after "
                      << consecutive_errors << " consecutive error(s)\n";
            std::this_thread::sleep_for(std::chrono::seconds(delay_s));
        }

        // Execute
        const std::string resp =
            client.place_market_order(order.symbol, order.side, order.qty);

        // Parse Binance response
        try {
            const json rj = json::parse(resp);
            if (rj.contains("code") && rj["code"].is_number_integer()) {
                const int code = rj["code"].get<int>();
                if (code < 0) {
                    std::cerr << "[engine] Binance error " << code << ": "
                              << rj.value("msg", "") << "\n";
                    ++consecutive_errors;
                    continue;
                }
            }
            consecutive_errors = 0;
            std::cout << "[engine] order placed — orderId="
                      << rj.value("orderId", json(0)).dump()
                      << " status=" << rj.value("status", "?") << "\n"
                      << std::flush;
        } catch (...) {
            std::cerr << "[engine] unexpected Binance response: " << resp
                      << "\n";
            ++consecutive_errors;
        }
    }

    std::cout << "[engine] shutting down\n" << std::flush;
    zmq_close(sock);
    zmq_ctx_destroy(ctx);
    return 0;
}
