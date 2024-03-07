import asyncio
import streamlit as st
import plotly.express as px
import logging

class MqttHandler:
    def __init__(self, address, port, topic):
        self.address = address
        self.port = port
        self.topic = topic
        self.data = {'time': [], 'value': []}  # Store received data
    async def start_handling(self):
        async with self.create_client() as client:
            await client.subscribe(self.topic)
            st.write("Listening for MQTT messages on topic:", self.topic)
            await self.listen_for_messages(client)

    async def listen_for_messages(self, client):
        async for message in client:
            try:
                value = message.payload.decode('utf-8')
                current_time = time.time()

                # Update the data dictionary
                self.data['time'].append(current_time)
                self.data['value'].append(float(value))

                # Update the Plotly chart
                fig = px.line(x=self.data['time'], y=self.data['value'], labels={'x': 'Time', 'y': 'Value'})
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                logging.error(f"Error processing MQTT message: {e}")

    async def create_client(self):
        return await asyncio.create_connection(self.address, self.port)

    async def stop_handling(self):
        pass  # No need to explicitly stop in aio-mqtt

    async def init(self):
        try:
            return True
        except Exception as e:
            logging.error(f"Error connecting to MQTT broker: {e}")
            st.error("Could not connect to MQTT broker. Please ensure the broker is running.")
            return False

    async def destroy(self):
        pass  # No need to explicitly disconnect in aio-mqtt

def mqtt_main():
    st.title("MQTT Visualizer")

    # User input for MQTT details
    broker = st.text_input("Enter MQTT Broker address:", key="broker_input")
    port = st.number_input("Enter MQTT Broker port:", min_value=1, max_value=65535, value=1883, key="port_input")
    topic = st.text_input("Enter MQTT Topic:", key="topic_input")

    if st.button("Start Visualization", key="start_button"):
        mqtt_handler = MqttHandler(broker, port, topic)
        if asyncio.run(mqtt_handler.init()):
            asyncio.run(mqtt_handler.start_handling())
            st.write("Visualization started. Waiting for MQTT messages...")
            if st.button("Stop Visualization", key="stop_button"):
                pass