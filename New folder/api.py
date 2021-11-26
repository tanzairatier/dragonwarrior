import digitalocean
import warnings

warnings.filterwarnings('ignore')


try:
    manager = digitalocean.Manager(token="0db699752723e35d100da8ea8fd6f7b9838f85fa09668478b9db3cb8a6c66b42")
    my_droplets = manager.get_all_droplets()
    print "Your droplet names:"
    for droplet in my_droplets:
        print " * " + droplet.name
except digitalocean.baseapi.DataReadError:
    print "Unable to authenticate you.  Your API key might be wrong!"
