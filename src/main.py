from config_manager import ConfigManager


if __name__ == "__main__":
    config_manager = ConfigManager("config.yaml")
    config = config_manager.data
    print(config)
