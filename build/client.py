import sys

def main(iParameters):
    print('iParameters:',iParameters)

    try:
        # Raise an exception with argument
        if not iParameters:
            raise Exception('Empty Parameter List')
    except Exception as error:
        # Catch exception
        print('Error: ', error)
  

if __name__ == "__main__":
    main(sys.argv[1:])