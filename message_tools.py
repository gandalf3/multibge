#!/usr/bin/env python3

def compose_message(message, recipient="CLIENT"):
    """
    Take an object of the form {"action": "", "uuid"} and pickle it.
    <strike>Also add timestamp</strike>
    """
    
    #message.append("timestamp": bge.logic.getFrameTime())
    
#    if recipient != "CLIENT":
#        return recipient + pickle.dumps(message)
#    else:
    
    return pickle.dumps(message)
    

def greet_server():
    greeting = compose_message({
        "recipient": "SERVER",
        "action": "CONNECT"
    })
    
    return greeting
    

def pickle_prep(m):
    """
    construct a pure python list representation of an iterable thingy
    (matrix, vector, etc)
    """
    
    list_representation = []
    if hasattr(m, '__len__'):
        for elem in m:
            list_representation.append(pickle_prep(elem))
        return list_representation
    else:
        return m
