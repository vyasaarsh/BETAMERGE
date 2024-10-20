import paramiko

# Function to establish SSH connection
def connect_ssh_agent(username): 
  hostname = "rt1.olsendata.com"
  port = 22103
  password = "aar5hvya5"
  ssh = paramiko.SSHClient()
  ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
  ssh.connect(hostname, port, username, password)
  return ssh.invoke_shell()

__all__ = ['connect_ssh_agent']
