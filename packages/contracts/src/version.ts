export const CONTRACT_PACKAGE_VERSION = "0.1.0";
export const CONTRACT_PROTOCOL_VERSION = "1.1.0";
export const CONTRACT_SCHEMA_VERSION_FILE = "schemas/generated/schema-version.json";

export interface ContractVersionInfo {
  packageVersion: string;
  protocolVersion: string;
  schemaVersionFile: string;
  generatedAt: "static";
}

export const CONTRACT_VERSION_INFO: ContractVersionInfo = Object.freeze({
  packageVersion: CONTRACT_PACKAGE_VERSION,
  protocolVersion: CONTRACT_PROTOCOL_VERSION,
  schemaVersionFile: CONTRACT_SCHEMA_VERSION_FILE,
  generatedAt: "static"
});
