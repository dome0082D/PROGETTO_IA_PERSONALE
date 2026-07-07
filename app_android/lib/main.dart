import 'package:flutter/material.dart';
import 'package:web_socket_channel/web_socket_channel.dart';

void main() => runApp(const MyApp());

class MyApp extends StatelessWidget {
  const MyApp({super.key});
  @override
  Widget build(BuildContext context) {
    return const MaterialApp(home: MonitorPage());
  }
}

class MonitorPage extends StatefulWidget {
  const MonitorPage({super.key});
  @override
  State<MonitorPage> createState() => _MonitorPageState();
}

class _MonitorPageState extends State<MonitorPage> {
  // Il canale deve puntare all'indirizzo dove Python si aspetta di connettersi
  final channel = WebSocketChannel.connect(Uri.parse('ws://localhost:8000/ws/windows'));

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Monitoraggio IA Personale")),
      body: StreamBuilder(
        stream: channel.stream,
        builder: (context, snapshot) {
          return Center(
            child: Text(snapshot.hasData ? '${snapshot.data}' : 'Monitoraggio IA attivo...'),
          );
        },
      ),
    );
  }

  @override
  void dispose() {
    channel.sink.close();
    super.dispose();
  }
}