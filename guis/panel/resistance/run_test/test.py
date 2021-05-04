def main():
    print("Test script")
    stop = False
    while not stop:
        print("Type something: ")
        message = input()
        if message == "stop":
            stop = True
        else:
            print("You typed: ", message)

    print("End of the test")


if __name__ == "__main__":
    main()
