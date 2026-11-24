# Misuse Case Diagram

```mermaid
flowchart LR
    User([Fitness User])
    OFF([Open Food Facts])
    Regulator([Data Regulator])
    Attacker([Attacker])

    subgraph Wger["wger system"]
        direction TB
        UC1([Create Workout Routine])
        UC2([Create Nutrition Plan])
        UC3([Track Body Weight])
        UC4([Log Cardio Activity])

        MC1{{Bypass Authentication}}
        MC2{{Read Another User's Data}}
        MC3{{Change Another User's Records}}

        C1[[Require Authenticated Access]]
        C2[[Restrict Access to Owned Data]]
        C3[[Validate Ownership of Submitted References]]
    end

    User --> UC1
    User --> UC2
    User --> UC3
    User --> UC4
    OFF -. ingredient data .-> UC2
    Regulator -. privacy interest .- UC1
    Regulator -. privacy interest .- UC2
    Regulator -. privacy interest .- UC3
    Regulator -. privacy interest .- UC4

    Attacker --> MC1
    Attacker --> MC2
    Attacker --> MC3

    MC1 -. threatens .-> UC1
    MC1 -. threatens .-> UC2
    MC1 -. threatens .-> UC3
    MC1 -. threatens .-> UC4
    MC2 -. threatens .-> UC1
    MC2 -. threatens .-> UC2
    MC2 -. threatens .-> UC3
    MC2 -. threatens .-> UC4
    MC3 -. threatens .-> UC1
    MC3 -. threatens .-> UC2
    MC3 -. threatens .-> UC3
    MC3 -. threatens .-> UC4

    C1 -. mitigates .-> MC1
    C2 -. mitigates .-> MC2
    C2 -. mitigates .-> MC3
    C3 -. mitigates .-> MC3

    classDef misuse fill:#ffe5e5,stroke:#b42318,color:#7a271a
    classDef control fill:#e8f5e9,stroke:#27834a,color:#174b2a
    class MC1,MC2,MC3 misuse
    class C1,C2,C3 control
```

## Security Control Evidence

- **Require Authenticated Access:** the measurement endpoints require `IsAuthenticated`; `RoutinePermission` also rejects unauthenticated requests. See `wger/measurements/api/views.py` and `wger/manager/api/permissions.py`.
- **Restrict Access to Owned Data:** measurement queries are filtered by the requesting user, and `RoutinePermission` limits private routines and workout history to their owner. See `wger/measurements/api/views.py` and `wger/manager/api/permissions.py`.
- **Validate Ownership of Submitted References:** `WgerOwnerObjectModelViewSet` checks foreign-key ownership before create and update operations. See `wger/utils/viewsets.py`.
