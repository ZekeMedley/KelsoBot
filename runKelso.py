from flask import Flask
import os
import subprocess

app = Flask(__name__)

# On Bluemix, get the port number from the environment variable VCAP_APP_PORT
# When running this app on the local machine, default the port to 8080
port = int(os.getenv('VCAP_APP_PORT', 8080))

@app.route('/')

def hello_world():
    print("CHECKING STREAM")
    checkp = subprocess.Popen("ps -ef | grep -i 'runKelso.py'", shell=True, stdout=subprocess.PIPE)
    (output, us) =  checkp.communicate()
    if "python" not in str(output) and "Python" not in str(output):
        print("TWITTER: Starting stream program")
        subprocess.Popen("python runKelso.py", shell=True)
        print('DISPATCH')
        return 'Dispatched WHOO'
    else:
        print(str(output))
        return str(output)


print("Starting server...")
app.run(host='0.0.0.0', port=port)
