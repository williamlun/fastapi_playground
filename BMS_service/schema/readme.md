``` mermaid
sequenceDiagram
    participant Client
    participant BMS Service
    participant BMS Service
    participant Database

    Client->>BMS Service: Request with above format
    BMS Service->>BMS Service: Generate target BMS request format base on above format
    BMS Service-->>Database: Log incoming request
    BMS Service->>BMS: Send request to target BMS
    BMS-->>BMS Service: Response
    BMS Service-->>Database: Log response
    BMS Service-->>Client: Response
```