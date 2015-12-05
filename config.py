config = {}

config["CONTROL_SERVER_IP"] = "116.251.217.98"
config["CONTROL_SERVER_PORT"] = 8080

# config about the server itself
config["SERVICE_QUOTA"] = 10
config["SERVER_LISTEN_PORT"] = 7129
config["SERVER_KEY"] = "demohndemohn"
config["SERVER_LOCATION"] = "SG"
config["VERSION"] = "0.1.1"

# SHADOWSOCKS MIN and MAX PORT
config["SHADOWSOCKS_MIN_PORT"] = 12000
config["SHADOWSOCKS_MAX_PORT"] = 15000
config["SS_DEFAULT_METHOD"] = "rc4-md5"
config["SS_DEFAULT_TIMEOUT"] = 100

# server working Limitation
config["MMAX_TRAFFIC"] = 100 * 1000 * 1000 * 1000
config["MMAX_DEVICES"] = 256