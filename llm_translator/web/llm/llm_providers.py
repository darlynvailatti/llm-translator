import dspy


def configure_dspy_lm():
    lm = dspy.LM(
        "openai/local-model",
        api_base="http://host.docker.internal:8080/v1",
        api_key="local",
        temperature=0,
    )
    dspy.configure(lm=lm)
