#!/usr/bin/python

import boto.ec2.autoscale
from flask import Flask
from flask import render_template
from flask import request
import subprocess32
import json
app = Flask(__name__)

reservation = None

@app.route('/')
def index():
    global reservation
    autoscale = boto.ec2.autoscale.AutoScaleConnection()
    ec2 = boto.ec2.connect_to_region('us-west-2')
    group = autoscale.get_all_groups(names=['Daala'])[0]
    num_instances = len(group.instances)
    instance_ids = [i.instance_id for i in group.instances]
    if len(instance_ids) > 0:
      instances = ec2.get_only_instances(instance_ids)
    else:
      instances = []
    return render_template('index.html',instances=instances,num_instances=num_instances, reservation=reservation)
    
@app.route('/start_instances')
def start_instances():
    autoscale = boto.ec2.autoscale.AutoScaleConnection()
    group = autoscale.get_all_groups(names=['Daala'])[0]
    autoscale.set_desired_capacity('Daala',2)
    return 'ok'
    
@app.route('/stop_instances')
def stop_instances():
    autoscale = boto.ec2.autoscale.AutoScaleConnection()
    group = autoscale.get_all_groups(names=['Daala'])[0]
    autoscale.set_desired_capacity('Daala',0)
    return 'ok'
    
@app.route('/get_machine_info')
def get_machine_info():
    autoscale = boto.ec2.autoscale.AutoScaleConnection()
    ec2 = boto.ec2.connect_to_region('us-west-2')
    group = autoscale.get_all_groups(names=['Daala'])[0]
    num_instances = len(group.instances)
    instance_ids = [i.instance_id for i in group.instances]
    if len(instance_ids) > 0:
      instances = ec2.get_only_instances(instance_ids)
    else:
      instances = []
    machines = []
    for instance in instances:
        machine = {}
        machine['id'] = instance.id
        machine['ip_address'] = instance.ip_address
        machine['state'] = instance.state
        machine['status'] = ec2.get_all_instance_status([instance.id])[0].instance_status.status
        machines.append(machine)
    return json.dumps(machines)
    
@app.route('/get_reservation')
def get_reservation():
    global reservation
    return reservation
    
@app.route('/make_reservation',methods=['POST'])
def make_reservation():
    global reservation
    if reservation is None:
        reservation = request.form['user']
        return 'ok'
    return 'fail'
        
@app.route('/clear_reservation')
def end_reservation():
    global reservation
    reservation = None
    return 'ok'
    
@app.route('/get_processes_running')
def get_processes_running():
    host = '54.191.180.122'
    try:
        return subprocess32.check_output(['ssh','-i','daala.pem','-o',' StrictHostKeyChecking=no','ec2-user@'+host,'ps -e | grep encoder_example'])
    except subprocess.CalledProcessError:
        return ''

if __name__ == '__main__':
    app.run(debug=True)

