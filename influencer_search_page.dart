import 'package:flutter/material.dart';
import 'algolia_service.dart';

class InfluencerSearchPage extends StatefulWidget {
  @override
  _InfluencerSearchPageState createState() => _InfluencerSearchPageState();
}

class _InfluencerSearchPageState extends State<InfluencerSearchPage> {
  List _results = [];
  final _controller = TextEditingController();

  Future<void> _search(String query) async {
    final Algolia algolia = AlgoliaService.algolia;

    AlgoliaQuery algoliaQuery = algolia.instance.index('influencers').query(query);
    AlgoliaQuerySnapshot snap = await algoliaQuery.getObjects();

    setState(() {
      _results = snap.hits;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text("Zoek een influencer")),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(8.0),
            child: TextField(
              controller: _controller,
              onChanged: _search,
              decoration: InputDecoration(
                labelText: "Typ een naam of bedrijf",
                border: OutlineInputBorder(),
              ),
            ),
          ),
          Expanded(
            child: ListView.builder(
              itemCount: _results.length,
              itemBuilder: (_, index) {
                final item = _results[index].data;
                return ListTile(
                  title: Text(item['naam'] ?? 'Zonder naam'),
                  subtitle: Text("Code: ${item['code'] ?? 'geen'} — Bedrijf: ${item['bedrijf'] ?? 'onbekend'}"),
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}
