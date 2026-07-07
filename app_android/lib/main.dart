import 'package:flutter/material.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'dart:convert';

void main() => runApp(const MyApp());

class MyApp extends StatelessWidget {
  const MyApp({super.key});
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      theme: ThemeData.dark(useMaterial3: true),
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
      body: StreamBuilder(
        stream: channel.stream,
        builder: (context, snapshot) {
          if (!snapshot.hasData) return const Center(child: CircularProgressIndicator());
          
          final Map<String, dynamic> dati = jsonDecode(snapshot.data);
          final mon = dati['monitoraggio'];
          
          return Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                // La "Riga Viva" che pulsa in base alla CPU
                Container(
                  height: 15,
                  width: (mon['cpu'] * 4).toDouble(),
                  decoration: BoxDecoration(
                    color: dati['sicurezza'] == "NORMALE" ? Colors.blue : Colors.red,
                    borderRadius: BorderRadius.circular(10)
                  ),
                ),
                const SizedBox(height: 40),
                Text("STATO: ${dati['sicurezza']}", style: const TextStyle(fontSize: 24)),
                Text("VISIONE: ${dati['visione']}", style: const TextStyle(fontSize: 18, color: Colors.grey)),
                const SizedBox(height: 20),
                Text("${mon['cpu'].toStringAsFixed(1)}%", style: const TextStyle(fontSize: 60, fontWeight: FontWeight.bold)),
              ],
            ),
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