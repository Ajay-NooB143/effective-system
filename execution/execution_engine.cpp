/**
 * Signals-only safety stub.
 *
 * Broker execution has been intentionally disabled. The historical C++
 * Binance order engine is replaced by this fail-closed entry point so old
 * binaries must be rebuilt before deployment.
 */
#include <iostream>

int main() {
    std::cerr << "[engine] BLOCKED: broker execution is disabled (signals-only mode).\n";
    return 2;
}
