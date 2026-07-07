import 'package:flutter/material.dart';
import 'package:web_socket_channel/web_socket_channel.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return const MaterialApp(
      home: MonitorPage(),
    );
  }
}

class MonitorPage extends StatefulWidget {
  const MonitorPage({super.key});

  @override
  State<MonitorPage> createState() => _MonitorPageState();
}

class _MonitorPageState extends State<MonitorPage> {
  // Connessione fissa alla porta 8080 aperta dal backend Python
  final channel = WebSocketChannel.connect(
    Uri.parse('ws://localhost:8080'),
  );

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Monitoraggio Reale"),
      ),
      body: Center(
        child: StreamBuilder(
          stream: channel.stream,
          builder: (context, snapshot) {
            if (snapshot.hasData) {
              return Text(
                'Dati Ricevuti: ${snapshot.data}',
                style: const TextStyle(
                  fontSize: 24, 
                  fontWeight: FontWeight.bold
                ),
              );
            } else if (snapshot.hasError) {
              return const Text(
                'Errore di connessione',
                style: TextStyle(color: Colors.red),
              );
            } else {
              return const Text(
                'In attesa del segnale...',
                style: TextStyle(fontSize: 20),
              );
            }
          },
        ),
      ),
    );
  }

  @override
  void dispose() {
    // Chiude il canale quando l'app viene chiusa
    channel.sink.close();
    super.dispose();
  }
}