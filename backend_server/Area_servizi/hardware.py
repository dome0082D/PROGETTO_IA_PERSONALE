import psutil
import platform

def get_hardware_status():
    # Rileva componenti reali
    cpu = platform.processor()
    ram = f"{round(psutil.virtual_memory().total / (1024**3), 2)} GB"
    dischi = psutil.disk_partitions()
    return {"cpu": cpu, "ram": ram, "dischi": [d.device for d in dischi]}