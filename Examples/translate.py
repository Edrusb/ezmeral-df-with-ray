#!/usr/bin/env python3

########################################################################
# translate.py - a simple script to install Ray on Linux
# Copyright (C) 2024 Denis Corbin
#
#  translate.py is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  translate.py is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Webdar.  If not, see <http://www.gnu.org/licenses/>
#
########################################################################

import sys
import ray
import requests
from starlette.requests import Request
import json

def usage(argv0):
    print("")
    print("   usage: {} launch {{ gpued | nogpu }} {{ <ray head IP> | job }} <instances>".format(argv0))
    print("   usage: {} ask    {{ gpued | nogpu }}   <ray head IP>          <message>".format(argv0))
    print("   usage: {} stop   {{ gpued | nogpu }} {{ <ray head IP> | job }}".format(argv0))
    print("")
    print("You can either launch and stop the model deployment either directly")
    print("connecting to the cluster providing the IP of the head node, or by")
    print("submitting a job, in which case you will have to use the \"job\"")
    print("in place of the IP of the Ray head")
    print("")
    print("Example: ray job submit --working-dir . -- python3 {} launch gpued job 1".format(argv0))
    print("   or  : ./{} launch df-1 1".format(argv0))
    print("")

def install_modules():
    import os
    os.system("pip install torch transformers")


def ray_init(ray_head_ip):
    if ray_head_ip == "job":
        ray.init()
    else:
        ray.init(address="ray://{}:10001".format(ray_head_ip))

def launch(ray_head_ip, num_instances, inf_port, inf_name, gpued):
    ray_init(ray_head_ip)

    from ray import serve
    from transformers import pipeline

    if gpued:
        numgpu=1/num_instances
    else:
        numgpu=0

    @serve.deployment(num_replicas=num_instances, ray_actor_options={"num_cpus": 1, "num_gpus": numgpu})
    class Translator:
        def __init__(self):
            # Load model
#            model="t5-small"
#            model="t5-base"
            model="t5-large"
            if gpued:
                self.model = pipeline("translation_en_to_fr", model=model, device=0)
            else:
                self.model = pipeline("translation_en_to_fr", model=model, device=-1)

        def translate(self, text: str) -> str:
            # Run inference
            model_output = self.model(text)

            # Post-process output to return only the translation text
            translation = model_output[0]["translation_text"]

            return translation

        async def __call__(self, http_request: Request) -> str:
            input_request = json.loads(await http_request.json())
            to_translate = input_request["src"]
            translated = self.translate(to_translate)
            output = { "src": to_translate, "dst": translated }
            return json.dumps(output)


    # first start ray serve if not already started

    serve.start(http_options = { 'host': "0.0.0.0", 'port': inf_port })

    # now deploy the model

    translator_app = Translator.bind()
    serve.run(target=translator_app, name=inf_name, route_prefix="/"+inf_name)
    ray.shutdown()

def ask(serve_ip, serv_port, inf_name, message):
    formatted_input = { "src": message }
    json_input = json.dumps(formatted_input)
    http_response = requests.post("http://{}:{}/{}".format(serve_ip, serv_port, inf_name), json=json_input)
    json_response = json.loads(http_response.text)
    print("\n\t{}\ntranslates to:\n\t{}\n".format(json_response["src"], json_response["dst"]))

def stop(ray_head_ip, inf_name):
    ray_init(ray_head_ip)

    from ray import serve

    serve.delete(inf_name)
    ray.shutdown()


def inf_name(gpued):
    if gpued:
        return "translate_gpued"
    else:
        return "translate_nogpu"


inf_port = 8000



if __name__ == "__main__":
    numarg = len(sys.argv)

    if numarg < 4:
        usage(sys.argv[0])
    else:
        action = sys.argv[1]
        gpued = sys.argv[2] == "gpued"
        head_or_job = sys.argv[3]

        if numarg == 4:
            arg = ""
        elif numarg == 5:
            arg = sys.argv[4]
        else:
            usage(sys.argv[0])

        if action == "launch":
            if numarg != 5:
                usage(sys.argv[0])
            else:
                num_inst = int(arg)
                install_modules()
                launch(head_or_job, num_inst, inf_port, inf_name(gpued), gpued)
        elif action == "ask":
            if numarg != 5:
                usage(sys.argv[0])
            else:
                ask(head_or_job, inf_port, inf_name(gpued), arg)
        elif action == "stop":
            if numarg != 4:
                usage(sys.argv[0])
            else:
                stop(head_or_job, inf_name(gpued))
        else:
            usage(sys.argv[0])
