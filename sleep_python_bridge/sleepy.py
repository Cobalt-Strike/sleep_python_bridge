from base64 import b64decode
from javaobj import loads


def wrap_command(command: str) -> str:
    """Wraps a sleep command in a Java serialization wrapper to conver the output to a serialized Java object.

    Args:
        command (str): The command to wrap in the wrapper.

    Returns:
        str: The wrapped sleep command.
    """    

    wrapper = """
    sub callback {
        {{COMMAND}};
    }

    import java.io.*; 
    import java.util.*; 
    $baos = [new ByteArrayOutputStream]; 
    $oos = [new ObjectOutputStream: $baos]; 
    [$oos writeObject: callback()]; 
    [$oos close]; 
    $encoder = [Base64 getEncoder]; 
    println([$encoder encodeToString: [$baos toByteArray]]);
    """

    # Replace command in wrapper
    wrapper = wrapper.replace(r"{{COMMAND}}", command)
    return convert_to_oneline(wrapper)


def convert_to_oneline(multiline: str) -> str:
    """Converts a multiline Sleep command to a single line.

    Args:
        multiline (str): The multiline Sleep command.

    Returns:
        str: A single-lined version of the same Sleep command.
    """    
    # Format wrapper so it sends as one-line
    oneline = multiline.replace('\n', '')
    # Replace 4 spaces with nothing (if tabbed but using spaces as tabs)
    nospaces = oneline.replace('    ', '')
    # Replace tabs with nothing
    notabs = nospaces.replace('\t', '')

    return notabs


def deserialize(serialized: str):
    """Deserializes a base64 Java serialized object.

    Args:
        serialized (str): The base64 Java serialized object to deserialize.

    Raises:
        Exception: An exception if one os thrown during deserializing. 
        Contains what exception was thrown and a preview of the data that threw the exception.

    Returns:
        Any: The python object of the Java serialized object.
    """    
    try:
        decoded = b64decode(serialized)
        return loads(decoded)
    except Exception as e:
        # If we raise an Exception in a try/except, it includes the original exception.
        # So we include from None to prevent this (and only raise a single exception)
        raise Exception(f"{type(e).__name__}: {e} raised on {serialized[:50]}") from None


def main():
    pass


if __name__ == "__main__":
    main()
