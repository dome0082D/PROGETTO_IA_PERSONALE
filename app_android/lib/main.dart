import 'package:flutter/material.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'dart:convert';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Monitoraggio IA Personale',
      theme: ThemeData(
        brightness: Brightness.dark,
        primarySwatch: Colors.blue,
        useMaterial3: true,
      ),
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
  // Canale di comunicazione WebSocket verso il server Python
  late WebSocketChannel channel;

  @override
  void initState() {
    super.initState();
    // Connessione esplicita all'indirizzo IP locale e porta 8080
    channel = WebSocketChannel.connect(
      Uri.parse('ws://127.0.0.1:8080'),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Monitoraggio IA Personale"),
        centerTitle: true,
      ),
      body: Center(
        child: StreamBuilder(
          stream: channel.stream,
          builder: (context, snapshot) {
            // Stato di errore nella connessione
            if (snapshot.hasError) {
              return Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.error, color: Colors.red, size: 60),
                  const SizedBox(height: 20),
                  Text('Errore: ${snapshot.error}', textAlign: TextAlign.center),
                ],
              );
            } 
            // Dati ricevuti correttamente
            else if (snapshot.hasData) {
              final Map<String, dynamic> dati = jsonDecode(snapshot.data);
              final cpu = dati['cpu'];
              final memoria = dati['memoria'];
              
              return Padding(
                padding: const EdgeInsets.all(20.0),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Icon(Icons.speed, size: 80, color: Colors.blue),
                    const SizedBox(height: 20),
                    Text(
                      "Utilizzo CPU: ${cpu['percentuale']}%",
                      style: const TextStyle(fontSize: 32, fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 10),
                    Text(
                      "Frequenza: ${cpu['frequenza']} MHz",
                      style: const TextStyle(fontSize: 20, color: Colors.grey),
                    ),
                    const Divider(height: 40),
                    Text(
                      "Utilizzo RAM: ${memoria['percentuale']}%",
                      style: const TextStyle(fontSize: 28),
                    ),
                    Text(
                      "Totale RAM: ${memoria['totale_gb']} GB",
                      style: const TextStyle(fontSize: 18, color: Colors.grey),
                    ),
                  ],
                ),
              );
            } 
            // Stato di attesa (loading)
            else {
              return const CircularProgressIndicator();
            }
          },
        ),
      ),
    );
  }

  @override
  void dispose() {
    // Chiusura sicura del canale per evitare memory leak
    channel.sink.close();
    super.dispose();
  }
}