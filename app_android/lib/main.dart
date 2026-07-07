import 'package:flutter/material.dart';
import 'package:web_socket_channel/web_socket_channel.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Monitoraggio IA',
      theme: ThemeData(primarySwatch: Colors.blue),
      home: const MonitorPage(),
    );
  }
}

class MonitorPage extends StatefulWidget {
  const MonitorPage({super.key});

  @override
  State<MonitorPage> createState() => _MonitorPageState();
}

class _MonitorPageState extends State<MonitorPage> {
  // Connessione fissa al server Python sulla porta 8080
  late WebSocketChannel channel;

  @override
  void initState() {
    super.initState();
    // Creazione del canale di comunicazione
    channel = WebSocketChannel.connect(
      Uri.parse('ws://localhost:8080'),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Monitoraggio IA Personale"),
      ),
      body: Center(
        child: StreamBuilder(
          stream: channel.stream,
          builder: (context, snapshot) {
            // Gestione dei diversi stati della connessione
            if (snapshot.hasError) {
              return const Text('Errore: Impossibile connettersi al server.');
            } else if (snapshot.hasData) {
              return Text(
                'Dati dal server: ${snapshot.data}',
                style: const TextStyle(fontSize: 20),
              );
            } else {
              return const Text('In attesa del segnale...', style: TextStyle(fontSize: 20));
            }
          },
        ),
      ),
    );
  }

  @override
  void dispose() {
    // Chiusura pulita della connessione alla chiusura dell'app
    channel.sink.close();
    super.dispose();
  }
}