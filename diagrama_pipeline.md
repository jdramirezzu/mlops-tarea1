# Diagrama del Pipeline MLOps — Predicción de Enfermedades

## Diagrama 1 — Pipeline completo end-to-end

```mermaid
flowchart TD
    subgraph SRC ["Fuentes de Datos"]
        A1["Registros Hospitalarios\nHCE"]
        A2["Bases Publicas\nUCI / PhysioNet"]
        A3["Orphanet / NIH\nEnf. huerfanas"]
        A4["Datos Sinteticos\nAugmentation / SMOTE"]
    end

    B["Ingesta al Data Lake"]
    C["Preprocesamiento\nLimpieza - Normalizacion - SMOTE - Feature Engineering"]
    D["Datos versionados — DVC"]

    SRC --> B --> C --> D

    D --> E1["Enf. comunes\nXGBoost / MLP"]
    D --> E2["Enf. huerfanas\nFew-Shot / Transfer Learning"]
    E1 --> F{"F1 macro\n>= umbral?"}
    E2 --> F
    F -- "No" --> G["Alerta equipo ML\nsin despliegue"]
    F -- "Si" --> H["Model Registry\nMLflow / DVC"]

    subgraph CICD ["CI/CD — GitHub Actions"]
        I["CI - cada PR\nflake8 - pytest - docker build"]
        J["CD - merge a main\ndocker push ghcr.io - smoke test staging"]
        I --> J
    end

    H --> I
    J -- "FAIL" --> K["Rollback\na imagen anterior"]
    J -- "OK" --> L{"Aprobacion\nManual"}
    L -- "Rechazado" --> M["Pipeline cancelado"]
    L -- "Aprobado" --> N["Deploy Produccion"]

    N --> O["Flask API — Docker\nlocalhost:5000"]

    subgraph MON ["Monitoreo"]
        P1["Data Drift"]
        P2["Model Drift"]
        P3["Feedback Medico"]
    end

    O --> MON
    P1 --> Q["Reentrenamiento\nmensual o por alerta de drift"]
    P2 --> Q
    P3 --> Q
    Q --> C

    classDef dataStyle  fill:#dbeafe,stroke:#3b82f6,color:#1e3a8a
    classDef modelStyle fill:#d1fae5,stroke:#10b981,color:#064e3b
    classDef cicdStyle  fill:#fef9c3,stroke:#ca8a04,color:#713f12
    classDef prodStyle  fill:#ede9fe,stroke:#7c3aed,color:#3b0764
    classDef monStyle   fill:#fee2e2,stroke:#ef4444,color:#7f1d1d
    classDef alertStyle fill:#fca5a5,stroke:#dc2626,color:#450a0a

    class A1,A2,A3,A4,B,C,D dataStyle
    class E1,E2,H modelStyle
    class I,J cicdStyle
    class N,O prodStyle
    class P1,P2,P3,Q monStyle
    class G,K,M alertStyle
```

---

## Diagrama 2 — Detalle del pipeline CI/CD con GitHub Actions

```mermaid
flowchart TD
    subgraph BRANCH ["Estrategia de Ramas"]
        FEAT["feature/* / hotfix/*\nexperiment/*"]
        DEV["develop\nintegracion continua"]
        MAIN["main\nproduccion estable"]
        FEAT -->|"PR + CI verde"| DEV
        DEV -->|"PR + CI verde + aprobacion"| MAIN
    end

    subgraph CI ["ci.yml — push o pull_request en cualquier rama"]
        C1["flake8\nlint"] --> C2["pytest\n12 tests"] --> C3["docker build\nverificacion"]
        C3 -- "todos verdes" --> C4["PR habilitado\npara merge"]
        C1 -- "FAIL" --> C5["PR bloqueado"]
        C2 -- "FAIL" --> C5
        C3 -- "FAIL" --> C5
    end

    subgraph CD ["cd.yml — push a main"]
        D1["docker build\n+ push a ghcr.io/:sha"] --> D2["smoke test\ncurl localhost:5000\nstaging"]
        D2 -- "FAIL" --> D3["Rollback\na imagen anterior"]
        D2 -- "OK" --> D4["Aprobacion manual\nGitHub Environment: production"]
        D4 -- "Aprobado" --> D5["Deploy\nProduccion"]
        D4 -- "Rechazado" --> D6["Pipeline cancelado"]
    end

    subgraph RETRAIN ["model-retrain.yml — schedule mensual o alerta de drift"]
        R1["Validar\ndatos nuevos"] --> R2["Entrenar\nmodelo"]
        R2 --> R3{"F1 macro\n>= umbral?"}
        R3 -- "No" --> R4["Alerta al equipo\nsin despliegue"]
        R3 -- "Si" --> R5["Push al\nmodel registry"]
        R5 --> R6["Actualizar imagen Docker\ndispara CD pipeline"]
    end

    MAIN -->|"trigger automatico"| CD
    BRANCH -.->|"trigger en cada push"| CI
    D5 -.->|"drift detectado en prod"| RETRAIN
    R6 -->|"nuevo modelo disponible"| CD

    classDef branchStyle fill:#f0fdf4,stroke:#16a34a,color:#14532d
    classDef ciStyle     fill:#fef9c3,stroke:#ca8a04,color:#713f12
    classDef cdStyle     fill:#ede9fe,stroke:#7c3aed,color:#3b0764
    classDef rtStyle     fill:#fee2e2,stroke:#ef4444,color:#7f1d1d
    classDef okStyle     fill:#d1fae5,stroke:#10b981,color:#064e3b
    classDef failStyle   fill:#fca5a5,stroke:#dc2626,color:#450a0a

    class FEAT,DEV,MAIN branchStyle
    class C1,C2,C3 ciStyle
    class C4 okStyle
    class C5,D3,D6,R4 failStyle
    class D1,D2,D4,D5 cdStyle
    class R1,R2,R3,R5,R6 rtStyle
```

---

> Los diagramas se renderizan automáticamente en GitHub. Para verlos localmente, usar [mermaid.live](https://mermaid.live).
