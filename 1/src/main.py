from kafka.admin import KafkaAdminClient

admin_client = KafkaAdminClient(
    bootstrap_servers=["localhost:9092", "localhost:9093"],
    client_id="admin"
)

print(admin_client.list_topics())