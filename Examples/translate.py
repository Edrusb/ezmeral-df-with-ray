#!/usr/bin/env python3

import sys
import ray
import requests
from starlette.requests import Request
import json

def usage(argv0):
    print("usage: {} launch {{ <ray head IP> | job }} <instances>".format(argv0))
    print("usage: {} ask    <ray head IP> <message>".format(argv0))
    print("usage: {} stop   {{ <ray head IP> | job }}".format(argv0))
    print("")
    print("You can lauch and stop the model deployment either directly")
    print("connecting to the cluster providing the IP of the head node, or by")
    print("submitting a job. In this case you will have to use the \"job\"")
    print("in place of the IP of the Ray head")
    print("")
    print("Example: RAY_ADDRESS="http://<head ip>:8265" ray job submit --working-dir . -- python3 {} launch job 1".format(argv0))
    print("   or  : {} launch <head ip> 1".format(argv0))
    print("")

def ray_init(ray_head_ip):
    if ray_head_ip == "job":
        ray.init()
    else:
        ray.init(address="ray://{}:10001".format(ray_head_ip))

def launch(ray_head_ip, num_instances, inf_port, inf_name):
    ray_init(ray_head_ip)

    from ray import serve
    from transformers import pipeline

    @serve.deployment(num_replicas=num_instances, ray_actor_options={"num_cpus": 1, "num_gpus": 0})
    class Translator:
        def __init__(self):
            # Load model
            self.model = pipeline("translation_en_to_fr", model="t5-small")

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


inf_port = 8000
inf_name = "translate"

if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[1] == "launch":
        ray_ip = sys.argv[2]
        num_inst = int(sys.argv[3])
        launch(ray_ip, num_inst, inf_port, inf_name)
    elif len(sys.argv) == 4 and sys.argv[1] == "ask":
        ray_ip = sys.argv[2]
        message = sys.argv[3]
        ask(ray_ip, inf_port, inf_name, message)
    elif len(sys.argv) == 3 and sys.argv[1] == "stop":
        ray_ip = sys.argv[2]
        stop(ray_ip, inf_name)
    else:
        usage(sys.argv[0])

