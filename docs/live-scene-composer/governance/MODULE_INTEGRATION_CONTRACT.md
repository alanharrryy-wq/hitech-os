# MODULE INTEGRATION CONTRACT

Modules extend the Composer without modifying the core.

## Requirements
Modules must:
- Register through the Module SDK
- Declare capabilities and dependencies
- Provide failure isolation

## Allowed Capabilities
Modules may:
- Extend inspector panels
- Add widget types
- Provide layout tools
- Respond to selection changes

## Forbidden Capabilities
Modules may NOT:
- Mutate runtime directly
- Modify scene contracts
- Override selection ownership