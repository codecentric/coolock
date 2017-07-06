# coolock - A coordinated locking wrapper script for distributed tasks
`coolock` is based on the [Tooz](https://github.com/openstack/tooz) Python
library. For a list of supported coordination backends see
[here](https://docs.openstack.org/developer/tooz/compatibility.html#locking).

The Tooz library is just an abstraction layer for different coordination
backends. Depending on the used backend you may need to install additional
python libraries. At the time of writing the following lock backends can be
used:

|Backend|Required Python PyPi Package(s)|
|:---    |:---                            |
|Consul|python-consul|
|etcd|(no additional packages required)|
|etcd3|etcd3|
|Memcached|pymemcache|
|MySQL|pymysql|
|Postgres|psycopg2|
|Redis|redis|
|Zookeeper|kazoo|
|File|(no additional packages required)|

In volatile distributed systems a common problem is to execute a certain
job just once for a number of nodes. Examples are backup cronjobs, sending
mails on a regular basis or reporting tasks. You want to execute those tasks
just once, no matter how many nodes your autoscaling mechanism has started at
the given point in time. Most distributed systems already depend on a
coordination backend like Apache ZooKeeper, Redis or Consul.
`coolock` offers an easy to use wrapper for those coordination backends,
that you can easily use for your tasksr, keeping the complexity of
coordination and even dealing with a coordination backend outside of
your scripts and crojobs.

*NOTE: This requires synced clocks to work as expected*

## Installation
`coolock` is available in the PyPI repository. Use pip to install it:
```
pip install coolock
```

## Usage
```
# Basic usage:
coolock --backend redis://localhost:6379 echo "Hello World"

# Running two instances on the same host. One will return immediately.
coolock --backend redis://localhost:6379 --node 1 echo "instance 1" &
coolock --backend redis://localhost:6379 --node 2 echo "instance 2" &
```

## Configuration file
You may also configure some or all parameters in a configuration file.
`coolock` looks for config files at `/etc/coolock` and `$HOME/coolock`.

Example configuration file:
```
# Coordination backend URI
coordination-backend: kazoo://localhost:2181

# Name of the lock to acquire
lock: coolock

# Wait at least guard-time (in seconds) to block other executions of the same job.
# If the execution of the command takes longer then the guard-time execution stops
# right after the command finishes.
guard-time: 30

# This nodes name. Default is the hostname.
# node: myhost

# Wait at least wait-timeout (in seconds) to acquire the lock
wait-timeout: 0

# Log file destination
log-file: /var/log/coolock.log

# Log level:
# Possible values are: debug, info, warning, error, critical
log-level: info

# Log file maximum size
log-max-size: 20971520 # 20 MB

# Number of rotated log copies to keep
rotate-log-copies: 5
```

## Similar Software
There are already some wrapper scripts that focus on a specific
coordination backend (that you might just not have in your setup):
* [cronsul](https://github.com/EvanKrall/cronsul): A simple bash script
  coordinator using HashiCorps Consul.
* [distributed-cron](https://github.com/whitehats/distributed-cron):
  Python script that is using a memcache client.
* [cron-lock](https://github.com/kvz/cronlock): A bash script that uses
  Redis for coordination.

