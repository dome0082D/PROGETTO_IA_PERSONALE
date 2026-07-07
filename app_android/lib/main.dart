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
      title: 'IA Personale - Sicurezza',
      theme: ThemeData(
        brightness: Brightness.dark,
        primarySwatch: Colors.blue,
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
  late WebSocketChannel channel;
  Map<String, dynamic> datiRicevuti = {};

  @override
  void initState() {
    super.initState();
    // Inizializzazione canale WebSocket verso Python
    channel = WebSocketChannel.connect(
      Uri.parse('ws://127.0.0.1:8080'),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Monitoraggio IA Personale")),
      body: Center(
        child: StreamBuilder(
          stream: channel.stream,
          builder: (context, snapshot) {
            if (snapshot.hasError) {
              return Text('Errore di connessione: ${snapshot.error}');
            } else if (snapshot.hasData) {
              datiRicevuti = jsonDecode(snapshot.data);
              return Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text("CPU: ${datiRicevuti['cpu']['percentuale']}%", 
                       style: const TextStyle(fontSize: 32)),
                  Text("Memoria: ${datiRicevuti['memoria']['percentuale']}%", 
                       style: const TextStyle(fontSize: 20)),
                ],
              );
            } else {
              return const CircularProgressIndicator();
            }
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