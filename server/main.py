import subprocess
from configparser import ConfigParser

from fastapi import FastAPI

app = FastAPI()
config = ConfigParser()

async def block(id, input_path):
  presharedkey =  open(f'{input_path}presharedkey-peer{id}').read()
  file = open(f'{input_path}peer{id}.conf').read().replace(presharedkey, presharedkey[::-1][2:] + '=' + '\n')

  with open(f'{input_path}peer{id}.conf', 'w') as f:
    f.write(file.strip())
  
  file = open('/root/wireguard/config/wg0.conf').read().replace(presharedkey, presharedkey[::-1][2:] + '=' + '\n')

  with open('/root/wireguard/config/wg0.conf', 'w') as f:
    f.write(file.strip())

  return reload_wireguard()

async def allow(id, input_path):
  presharedkey =  open(f'{input_path}presharedkey-peer{id}').read().replace('\n', '')

  file = open(f'{input_path}peer{id}.conf').read().replace(presharedkey[::-1][1:] + '=', presharedkey)

  with open(f'{input_path}peer{id}.conf', 'w') as f:
    f.write(file.strip())
  
  file = open('/root/wireguard/config/wg0.conf').read().replace(presharedkey[::-1][1:] + '=', presharedkey)

  with open('/root/wireguard/config/wg0.conf', 'w') as f:
    f.write(file.strip())
  
  return reload_wireguard()


async def generate(id, input_path):
  presharedkey =  open(f'{input_path}presharedkey-peer{id}').read()

  subprocess.check_output(f'docker exec -t wireguard wg genkey > {input_path}presharedkey-peer{id}', shell=True)

  new_presharedkey = open(f'{input_path}presharedkey-peer{id}').read()

  file = open(f'{input_path}peer{id}.conf').read().replace(presharedkey, new_presharedkey)

  with open(f'{input_path}peer{id}.conf', 'w') as f:
    f.write(file.strip())
  
  file = open('/root/wireguard/config/wg0.conf').read().replace(presharedkey, new_presharedkey)

  with open('/root/wireguard/config/wg0.conf', 'w') as f:
    f.write(file.strip())
  
  return reload_wireguard()


async def change_preshared_key(controller, id):
  path = f"/root/wireguard/config/peer{id}/"
  controllers = {
    'allow': allow, 
    'block': block,
    'generate': generate
  }
  return await controllers[controller](id, path)

def reload_wireguard():
  subprocess.Popen(args=["docker", "exec","-t","wireguard","wg-quick","down","wg0"], stdout=subprocess.PIPE)
  subprocess.Popen(args=["docker", "exec","-t","wireguard","wg-quick","up","wg0"], stdout=subprocess.PIPE)

@app.get('/address/block')
async def block_address(id: int):
  await change_preshared_key(controller='block', id=id)

@app.get('/address/allow')
async def allow_address(id: int):
  await change_preshared_key(controller='allow', id=id)

@app.get('/address/generate')
async def generate_address(id: int):
  await change_preshared_key(controller='generate', id=id)
