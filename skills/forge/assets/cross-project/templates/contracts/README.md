# Cross-Project Contracts

Contract docs describe authority-owned shared shapes that peer or downstream
repos depend on.

Add one file per contract. Keep each file focused on:

- authoritative source files
- current shape
- stability promise
- compatibility expectations
- change protocol
- linked XPDs

Breaking or externally visible changes to authority-owned contracts require an
XPD unless project policy explicitly records a smaller exception path.
