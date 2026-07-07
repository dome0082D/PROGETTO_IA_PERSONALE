import 'package:flutter/material.dart';
import 'package:web_socket_channel/web_socket_channel.dart';

void main() => runApp(const MaterialApp(home: MonitorPage()));

class MonitorPage extends StatefulWidget {
  const MonitorPage({super.key});

  @override
  State<MonitorPage> createState() => _MonitorPageState();
}

class _MonitorPageState extends State<MonitorPage> {
  // Questa è la chiave: puntiamo alla 8080 fissa, NON al localhost di Chrome
  final channel = WebSocketChannel.connect(Uri.parse('ws://127.0.0.1:8080'));

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Monitoraggio Fisso")),
      body: Center(
        child: StreamBuilder(
          stream: channel.stream,
          builder: (context, snapshot) {
            if (snapshot.hasData) {
              return Text('Dati: ${snapshot.data}', style: const TextStyle(fontSize: 30));
            }
            return const Text('In attesa della porta 8080...');
          },
        ),
      ),
    );
  }

  @override
  void dispose() {
    channel.sink.close();
    super.dispose();
  }
}