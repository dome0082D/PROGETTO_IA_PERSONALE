import 'package:flutter/material.dart';
import 'package:web_socket_channel/web_socket_channel.dart';

void main() => runApp(const MyApp());

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: Scaffold(
        appBar: AppBar(title: const Text("Monitoraggio IA Personale")),
        body: const Center(child: MonitoraggioWidget()),
      ),
    );
  }
}

class MonitoraggioWidget extends StatefulWidget {
  const MonitoraggioWidget({super.key});
  @override
  State<MonitoraggioWidget> createState() => _MonitoraggioWidgetState();
}

class _MonitoraggioWidgetState extends State<MonitoraggioWidget> {
  // L'app si mette in ascolto sulla porta 8080
  final channel = WebSocketChannel.connect(Uri.parse('ws://localhost:8080/ws/windows'));

  @override
  Widget build(BuildContext context) {
    return StreamBuilder(
      stream: channel.stream,
      builder: (context, snapshot) {
        return Text(
          snapshot.hasData ? '${snapshot.data}' : 'Monitoraggio IA attivo...',
          style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
        );
      },
    );
  }
}