# Plan-Net Data Model — Proposed Changes

The diagram below shows the three Plan-Net resources affected by this proposal
and every element-level change. Node colour indicates the nature of each change.

```mermaid
flowchart TB
    classDef existing  fill:#dbeafe,stroke:#3b82f6,color:#1e3a5f
    classDef added     fill:#dcfce7,stroke:#16a34a,color:#14532d
    classDef promoted  fill:#fef9c3,stroke:#ca8a04,color:#713f12
    classDef codesys   fill:#fce7f3,stroke:#db2777,color:#831843

    subgraph ORG["plannet-Organization"]
        Oex["active · name · type · address · partOf\n(no change)"]
        O1["P1 — ADD identifier:FPI  1..1 MS"]
        O2["P2 — PROMOTE identifier:HIOS, NAIC → MS"]
        O3["P3 — ADD telecom:url  1..1 MS"]
        O4["P4 — PROMOTE alias → 0..* MS  (send if known)"]
    end

    subgraph IP["plannet-InsurancePlan"]
        IPex["status · type · name MS · alias MS · ownedBy MS\n(no change)"]
        P5["P5 — ADD contact.telecom:url  1..1 MS"]
    end

    subgraph EP["plannet-Endpoint"]
        EPex["status · connectionType · address\n(no change)"]
        E6["P6 — PROMOTE endpoint-usecase → MS"]
        subgraph EU["endpoint-usecase extension"]
            E7A["P7A — REBIND type → PlanNetEndpointTypeCS\n        PROMOTE standard → 1..1 MS  (recommended)"]
            E7B["P7B — OR: ADD new endpoint-ig-conformance\n        extension with ig-type + ig-version  (alternative)"]
        end
        E8["P8 — DOCUMENT multiple-version pattern\n(one Endpoint resource per IG version)"]
    end

    subgraph CS["NEW  PlanNetEndpointTypeCS"]
        Cc["davinci-crd  ·  davinci-pas  ·  davinci-cdex\ndavinci-pdex-formulary  ·  davinci-payer-to-payer\ndavinci-pdex-patient-access  ·  davinci-pdex-provider-directory\ncarin-bluebutton  ·  carin-rtpbc\none code per named IG — version lives in standard field"]
    end

    IP -- "ownedBy  1..1 MS" --> ORG
    ORG -- "endpoint  0..* MS" --> EP
    E7A -. "type bound to" .-> CS
    E7B -. "ig-type bound to" .-> CS

    class Oex,IPex,EPex existing
    class O1,O3,P5,E7B added
    class O2,O4,E6,E7A promoted
    class CS,Cc codesys
```

## Legend

| Colour | Meaning |
|---|---|
| 🔵 Blue | Existing element — no change required |
| 🟢 Green | New element or slice being added |
| 🟡 Yellow | Existing element being promoted to MustSupport |
| 🩷 Pink | New CodeSystem being defined |
