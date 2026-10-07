# HookForge Architecture

`evaluate_receiver` is the scorecard. `simulate_delivery` is the deterministic replay engine. The system intentionally keeps the simulation local so the portfolio evidence is inspectable and safe.

The receiver model separates baseline engineering capabilities from scenario pressure. A receiver can have an 80-point baseline and still lose points when a selected failure mode exposes a missing control.
