from src.infra_fail_mngr.wire import wire


def main():
    agent = wire()
    agent.run_to_completion()


if __name__ == "__main__":
    main()
