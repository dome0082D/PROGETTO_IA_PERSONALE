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
  // Canale di connessione
  final channel = WebSocketChannel.connect(
    Uri.parse('ws://localhost:8000/ws/windows'),
  );

  @override
  void dispose() {
    channel.sink.close();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return StreamBuilder(
      stream: channel.stream,
      builder: (context, snapshot) {
        if (snapshot.hasError) {
          return const Text('Errore di connessione');
        } else if (snapshot.hasData) {
          return Text(
            'Dati Ricevuti: ${snapshot.data}',
            style: const TextStyle(fontSize: 20),
          );
        } else {
          return const Text('Monitoraggio IA attivo...');
        }
      },
    );
  }
}