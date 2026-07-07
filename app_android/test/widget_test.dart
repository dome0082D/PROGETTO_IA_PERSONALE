import 'package:flutter_test/flutter_test.dart';
import 'package:app_android/main.dart'; 

void main() {
  testWidgets('Test avvio app IA Personale', (WidgetTester tester) async {
    // Carica la nostra applicazione
    await tester.pumpWidget(const AppPersonale());

    // Verifica che l'app contenga il testo atteso
    expect(find.text('Monitoraggio IA attivo'), findsOneWidget);
  });
}