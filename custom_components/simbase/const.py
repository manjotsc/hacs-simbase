"""Constants for the Simbase integration."""

DOMAIN = "simbase"

# API Constants
API_BASE_URL = "https://api.simbase.com/v2"
API_ENDPOINT_SIMCARDS = "/simcards"
API_ENDPOINT_USAGE = "/usage/simcards"
API_ENDPOINT_EVENTS = "/events"
API_ENDPOINT_ACCOUNT = "/account"
API_ENDPOINT_BALANCE = "/account/balance"

# Configuration
CONF_API_KEY = "api_key"
CONF_SCAN_INTERVAL = "scan_interval"

# Sensor options
CONF_ENABLE_SENSORS = "enable_sensors"
CONF_ENABLE_BINARY_SENSORS = "enable_binary_sensors"
CONF_ENABLE_SWITCH = "enable_switch"

# Sensor keys
SENSOR_DATA_USAGE = "data_usage"
SENSOR_DATA_LIMIT = "data_limit"
SENSOR_STATUS = "status"
SENSOR_NETWORK = "network"
SENSOR_SIGNAL_STRENGTH = "signal_strength"
SENSOR_CONNECTION_TYPE = "connection_type"
SENSOR_IP_ADDRESS = "ip_address"
SENSOR_ICCID = "iccid"
SENSOR_IMEI = "imei"
SENSOR_MSISDN = "msisdn"
SENSOR_PLAN = "plan"
SENSOR_MONTHLY_COST = "monthly_cost"
SENSOR_SMS_COUNT = "sms_count"
SENSOR_SMS_SENT = "sms_sent"
SENSOR_SMS_RECEIVED = "sms_received"
SENSOR_HARDWARE = "hardware"

# Binary sensor keys
BINARY_SENSOR_ONLINE = "online"
BINARY_SENSOR_DATA_LIMIT_EXCEEDED = "data_limit_exceeded"
BINARY_SENSOR_THROTTLED = "throttled"
BINARY_SENSOR_ROAMING = "roaming"

# All available sensors with display names
AVAILABLE_SENSORS = {
    SENSOR_DATA_USAGE: "Data Usage",
    SENSOR_STATUS: "Status",
    SENSOR_PLAN: "Coverage Plan",
    SENSOR_MONTHLY_COST: "Monthly Cost",
    SENSOR_SMS_COUNT: "SMS Total",
    SENSOR_SMS_SENT: "SMS Sent",
    SENSOR_SMS_RECEIVED: "SMS Received",
    SENSOR_HARDWARE: "Hardware",
    SENSOR_ICCID: "ICCID",
    SENSOR_IMEI: "IMEI",
    SENSOR_MSISDN: "Phone Number (MSISDN)",
    SENSOR_IP_ADDRESS: "IP Address",
    # These are not available in Simbase API:
    # SENSOR_DATA_LIMIT: "Data Limit",
    # SENSOR_NETWORK: "Network Operator",
    # SENSOR_SIGNAL_STRENGTH: "Signal Strength",
    # SENSOR_CONNECTION_TYPE: "Connection Type",
}

AVAILABLE_BINARY_SENSORS = {
    BINARY_SENSOR_ONLINE: "Online Status",
    # These are not available in Simbase API:
    # BINARY_SENSOR_DATA_LIMIT_EXCEEDED: "Data Limit Exceeded",
    # BINARY_SENSOR_THROTTLED: "Throttled",
    # BINARY_SENSOR_ROAMING: "Roaming",
}

# Default enabled sensors
DEFAULT_SENSORS = [
    SENSOR_DATA_USAGE,
    SENSOR_STATUS,
    SENSOR_PLAN,
    SENSOR_MONTHLY_COST,
]

DEFAULT_BINARY_SENSORS = [
    BINARY_SENSOR_ONLINE,
]

DEFAULT_ENABLE_SWITCH = True

# Defaults
DEFAULT_SCAN_INTERVAL = 300  # 5 minutes

# Platforms
PLATFORMS = ["sensor", "binary_sensor", "switch", "button"]

# SIM States
SIM_STATE_ACTIVE = "active"
SIM_STATE_INACTIVE = "inactive"
SIM_STATE_SUSPENDED = "suspended"

# Attributes
ATTR_ICCID = "iccid"
ATTR_IMEI = "imei"
ATTR_MSISDN = "msisdn"
ATTR_DATA_USAGE = "data_usage"
ATTR_DATA_LIMIT = "data_limit"
ATTR_SIM_STATE = "sim_state"
ATTR_NETWORK = "network"
ATTR_COUNTRY = "country"
ATTR_PLAN = "plan"
ATTR_LAST_SEEN = "last_seen"

# Services
SERVICE_ACTIVATE_SIM = "activate_sim"
SERVICE_DEACTIVATE_SIM = "deactivate_sim"
SERVICE_SEND_SMS = "send_sms"
SERVICE_READ_SMS = "read_sms"
