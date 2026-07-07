import 'package:flutter_test/flutter_test.dart';
import '../lib/main.dart'; // Import relativo al file main.dart

void main() {
  testWidgets('Test avvio app IA Personale', (WidgetTester tester) async {
    // Carica la nostra applicazione
    await tester.pumpWidget(const AppPersonale());

    // Verifica che il testo che definisce l'interfaccia sia presente
    expect(find.text('Monitoraggio IA attivo'), findsOneWidget);
  });
}