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
      theme: ThemeData(brightness: Brightness.dark, useMaterial3: true),
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

  @override
  void initState() {
    super.initState();
    channel = WebSocketChannel.connect(Uri.parse('ws://127.0.0.1:8080'));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Monitoraggio IA Personale"), centerTitle: true),
      body: Center(
        child: StreamBuilder(
          stream: channel.stream,
          builder: (context, snapshot) {
            if (snapshot.hasError) {
              return Text('Errore di connessione: ${snapshot.error}');
            } else if (snapshot.hasData) {
              // CORREZIONE: Mappatura corretta con il nuovo schema del backend
              final Map<String, dynamic> dati = jsonDecode(snapshot.data);
              final monitoraggio = dati['monitoraggio'];
              final statoSicurezza = dati['sicurezza'];
              
              return Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text("Sicurezza: $statoSicurezza", style: TextStyle(
                    color: statoSicurezza == "NORMALE" ? Colors.green : Colors.red,
                    fontSize: 20
                  )),
                  const SizedBox(height: 20),
                  Text("Utilizzo CPU: ${monitoraggio['cpu']}%", style: const TextStyle(fontSize: 32)),
                  Text("Utilizzo RAM: ${monitoraggio['ram']}%", style: const TextStyle(fontSize: 28)),
                ],
              );
            }
            return const CircularProgressIndicator();
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