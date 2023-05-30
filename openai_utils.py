# !/usr/bin/env python3
# _*_ coding:utf-8 _*_
import openai
import random
import time



def create_response( eng,prompt_input, max_tokens=256, temperature=0.0, stop=None):
    if stop is None:
        response = openai.Completion.create(
            model=eng,
            prompt=prompt_input,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            # stop=["{}:".format(stop)]
        )
        # print(response)
    else:
        response = openai.Completion.create(
            model=eng,
            prompt=prompt_input,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            stop=["{}:".format(stop)]
        )
    return response


def create_response_chat(eng="gpt-3.5-turbo", prompt_input=None, max_tokens=256, temperature=0.0, stop="Q"):
    response = openai.ChatCompletion.create(
        model=eng,
        messages=prompt_input,
        temperature=temperature,
    )
    return response
