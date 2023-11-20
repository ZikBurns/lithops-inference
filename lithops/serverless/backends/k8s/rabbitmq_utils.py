import pika
import json
import logging
from multiprocessing import Value


logger = logging.getLogger(__name__)


class RabbitMQ_utils:
    def __init__(self, amqp_url):
        params = pika.URLParameters(amqp_url)
        self.connection = pika.BlockingConnection(params)
        self.channel = self.connection.channel()

        self.total_cluster_cpus = 0
        self.range_id_begin = Value('i', 0)

        self.channel.queue_declare(queue='id-assignation')
        self.channel.basic_consume(queue='id-assignation', on_message_callback=self._assign_id, auto_ack=True)

    # Function to assign ID ranges
    def _assign_id(self, ch, method, properties, body):
        message             = json.loads(body)
        num_cpus            = message["num_cpus"]
        data_reception_id   = message["data_reception_id"]

        msg = { 
                "range_start" : self.range_id_begin.value,
                "range_end"   : self.range_id_begin.value + num_cpus -1,
                "total_cpus"  : self.total_cluster_cpus
            }

        self.range_id_begin.value = self.range_id_begin.value + num_cpus
        self.channel.basic_publish(exchange='', routing_key=data_reception_id, body=json.dumps(msg))

        if self.total_cluster_cpus <= self.range_id_begin.value:
            self.channel.stop_consuming()
            logger.debug("Closing channel")
            self.connection.close()

    # Start the assignation of IDs to each CPU
    def _start_cpu_assignation(self, n_procs):
        self.total_cluster_cpus = n_procs
        
        logger.info(f"Total cpus of the cluster: {self.total_cluster_cpus}")
        if self.total_cluster_cpus == 0:
            raise ValueError("Total CPUs of the cluster cannot be 0")
        
        self.channel.start_consuming()
