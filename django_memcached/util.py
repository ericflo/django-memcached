import datetime

try:
    import memcache
    memcache_installed = True
except ImportError:
    memcache_installed = False

def get_memcached_stats(server):
    if not memcache_installed:
        return {}
    host = memcache._Host(server)
    host.connect()
    host.send_cmd("stats")
    
    stats = {}
    
    while True:
        try:
            stat, key, value = host.readline().split(None, 2)
        except ValueError:
            break
        try:
            # Convert to native type, if possible
            value = int(value)
            if key == "uptime":
                value = datetime.timedelta(seconds=value)
            elif key == "time":
                value = datetime.datetime.fromtimestamp(value)
        except ValueError:
            pass
        stats[key] = value

    host.close_socket()
    
    try:
        stats['hit_rate'] = 100 * stats['get_hits'] / stats['cmd_get']
    except ZeroDivisionError:
        stats['hit_rate'] = stats['get_hits']
    
    return stats