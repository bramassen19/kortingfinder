import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:flutter/services.dart';
import 'package:algolia/algolia.dart';

void main() => runApp(KortingFinderApp());

class KortingFinderApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'KortingFinder',
      theme: ThemeData(primarySwatch: Colors.purple),
      home: HomePage(),
      debugShowCheckedModeBanner: false,
    );
  }
}

class HomePage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
      length: 2,
      child: Scaffold(
        appBar: AppBar(
          title: Text('KortingFinder'),
          bottom: TabBar(
            tabs: [
              Tab(text: 'Algolia AI'),
            ],
          ),
        ),
        body: TabBarView(
          children: [
            AlgoliaZoeker(),
          ],
        ),
      ),
    );
  }
}

/// 🔍 Algolia AI Zoeker
class AlgoliaZoeker extends StatefulWidget {
  @override
  _AlgoliaZoekerState createState() => _AlgoliaZoekerState();
}

class _AlgoliaZoekerState extends State<AlgoliaZoeker> {
  final TextEditingController _controller = TextEditingController();
  final Algolia _algolia = Algolia.init(
    applicationId: 'E51E1ZIN4O',
    apiKey: '9d15da91ccac3f3e3c7ec0710061dd1d',
  );

  List<AlgoliaObjectSnapshot> _resultaten = [];

  void _zoek() async {
    final query = _controller.text.trim();
    if (query.isEmpty) return;

    final resultaat = await _algolia.instance
        .index('influencers')
        .query(query)
        .getObjects();

    setState(() {
      _resultaten = resultaat.hits;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          TextField(
            controller: _controller,
            decoration: InputDecoration(
              labelText: 'Zoek influencer of merk (bv. Gymshark)',
              border: OutlineInputBorder(),
            ),
            onSubmitted: (_) => _zoek(),
          ),
          const SizedBox(height: 12),
          ElevatedButton(onPressed: _zoek, child: Text('Zoek via Algolia')),
          const SizedBox(height: 16),
          Expanded(
            child: _resultaten.isEmpty
                ? Center(child: Text('Nog geen resultaten gevonden.'))
                : ListView.builder(
                    itemCount: _resultaten.length,
                    itemBuilder: (_, i) {
                      final data = _resultaten[i].data;
                      return ListTile(
                        title: Text(data['naam'] ?? ''),
                        subtitle: Text('Code: ${data['code'] ?? ''}'),
                        trailing: Text(data['bedrijf'] ?? ''),
                      );
                    },
                  ),
          ),
        ],
      ),
    );
  }
}

/// 📄 Handmatige JSON Zoeker
class KortingscodeZoeker extends StatefulWidget {
  @override
  _KortingscodeZoekerState createState() => _KortingscodeZoekerState();
}

class _KortingscodeZoekerState extends State<KortingscodeZoeker> {
  final TextEditingController _controller = TextEditingController();
  String _winkel = '';

  Future<List<Map<String, dynamic>>> fetchKortingscodes(String winkel) async {
    final url = Uri.parse("https://kortingfinder.web.app/kortingscodes.json");
    final resp = await http.get(url);
    if (resp.statusCode != 200) {
      throw Exception("Kon kortingscodes niet laden (${resp.statusCode})");
    }
    final data = jsonDecode(resp.body);
    final List all = data["kortingscodes"];
    return all
        .where((item) =>
            (item["bedrijf"] as String).toLowerCase() ==
            winkel.toLowerCase())
        .cast<Map<String, dynamic>>()
        .toList();
  }

  void _startZoeken() {
    final winkelInput = _controller.text.trim();
    if (winkelInput.isNotEmpty) {
      setState(() {
        _winkel = winkelInput;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          TextField(
            controller: _controller,
            decoration: InputDecoration(
              labelText: 'Winkelnaam (bijv. Zalando)',
              border: OutlineInputBorder(),
            ),
            onSubmitted: (_) => _startZoeken(),
          ),
          const SizedBox(height: 12),
          ElevatedButton(onPressed: _startZoeken, child: Text('Zoek korting')),
          const SizedBox(height: 16),
          Expanded(
            child: _winkel.isEmpty
                ? Center(child: Text('Typ een winkelnaam om te zoeken.'))
                : FutureBuilder<List<Map<String, dynamic>>>(
                    future: fetchKortingscodes(_winkel),
                    builder: (ctx, snap) {
                      if (snap.connectionState == ConnectionState.waiting) {
                        return Center(child: CircularProgressIndicator());
                      }
                      if (snap.hasError) {
                        return Center(
                            child: Text('Fout: ${snap.error.toString()}'));
                      }

                      final codes = snap.data!;
                      if (codes.isEmpty) {
                        return Center(
                          child: Text(
                            'Geen werkende codes gevonden voor $_winkel.',
                            textAlign: TextAlign.center,
                            style: TextStyle(fontStyle: FontStyle.italic),
                          ),
                        );
                      }

                      return ListView.separated(
                        itemCount: codes.length,
                        separatorBuilder: (_, __) => Divider(),
                        itemBuilder: (_, i) {
                          final c = codes[i];
                          return ListTile(
                            title: Text(c['code'] ?? ''),
                            subtitle: Text(c['geldig_tot'] ?? ''),
                            trailing: IconButton(
                              icon: Icon(Icons.copy),
                              onPressed: () {
                                Clipboard.setData(
                                    ClipboardData(text: c['code']));
                                ScaffoldMessenger.of(context).showSnackBar(
                                  SnackBar(content: Text('Code gekopieerd!')),
                                );
                              },
                            ),
                          );
                        },
                      );
                    },
                  ),
          ),
        ],
      ),
    );
  }
}
