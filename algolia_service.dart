import 'package:algolia/algolia.dart';

class AlgoliaService {
  static final Algolia _algolia = const Algolia.init(
    applicationId: 'E51E1ZIN4O', // Jouw Algolia App ID
    apiKey: '9d15da91ccac3f3e3c7ec0710061dd1d', // Alleen de **Search-Only API Key**, NIET de Admin Key!
  );

  static Algolia get algolia => _algolia;
}
