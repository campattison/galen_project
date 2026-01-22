# Translation Evaluation: On Comp

**Generated:** 2026-01-22 09:20

This document provides a side-by-side comparison of translations and their evaluation scores for validation and transparency.

## Summary

### Overall Rankings

| Rank | Model | Score |
|------|-------|-------|
| 🥇 1 | GEMINI | 0.5494 |
| 🥈 2 | CLAUDE | 0.5382 |
| 🥉 3 | OPENAI | 0.5218 |

### Methodology

- **BLEU-4, chrF++, METEOR**: Multi-reference (n-grams matched against ANY reference)
- **ROUGE-L, BERTScore, COMET**: Max score across references

---

## Chunk-by-Chunk Analysis

### Chunk 1

#### Source (Greek)

> Περὶ μὲν τῆς τῶν ἁπλῶν φαρμάκων δυνάμεως εἴρηται δι’ ἑτέρας πραγματείας ὅτι χρὴ γινώσκειν ἑκάστου τὴν δύναμιν, οὐ κατὰ γένος μόνον, ὡς ἔγραψάν τινες, ἤτοι θερμαίνειν ἢ ψύχειν ἢ ξηραίνειν ἢ ὑγραίνειν εἰπόντες, ἀλλὰ διωρισμένως τε καὶ διηρθρωμένως, ἐκ τίνος ἐστὶ τάξεως, ὡς ἡμεῖς ἐδηλώσαμεν. ἔνια μὲν γὰρ φάρμακα παντάπασιν ἀμυδρῶς ἐργάζεται τῶν εἰρημένων ἕκαστον, ἔνια δὲ σαφῶς, ἔνια δὲ ἰσχυρῶς, ὥσπερ ἄλλα τελέως. οὔκουν αὐταρκὲς ἐπίστασθαι θερμαίνειν ἢ ψύχειν τόδε τὸ φάρμακον, ἀλλὰ καὶ μέχρι πόσου θερμαίνει καὶ ψύχει προσδιορίσασθαι χρή. θερμαίνουσι γὰρ αἱ ῥητίναι πᾶσαι καὶ τοῦτο κοινὸν αὐταῖς, ἀλλὰ τὸ μᾶλλον καὶ ἧττον οὐκ ὀλίγον ἐν τῇ θερμότητι κέκτηνται. θερμαίνουσι δὲ καὶ ὀποὶ πολλοὶ, διαφέροντες ἀλλήλων οὐ σμικρὰν διαφορὰν ἐν τῷ μᾶλλόν τε καὶ ἧττον. εἰ γὰρ παραβάλλοις ὀπὸν πάνακος τῷ Κυρη...

#### Reference Translations

**Reference 1:**
> Regarding the properties of simple drugs, in another work it has been stated that one must know the capacity of each, not only according to kind – as some have written, saying [simply] that they warm, cool, dry, or moist – but, as we have shown, specifically and distinctly by which degree. For some of the remedies mentioned act rather imperceptibly, some clearly, some strongly, while others fully. One must not [only] know whether that specific drug warms or cools sufficiently but must also specify to what extent it warms or cools. For all resins warm and this is common to [all of] them, but th...

#### Model Translations & Scores

**CLAUDE**

> Concerning the power of simple drugs, it has been stated in another treatise that one must know the power of each, not only according to genus, as some have written, merely saying that it heats or cools or dries or moistens, but in a distinguished and articulated manner, to what degree it belongs, as we have demonstrated. For some drugs produce each of the aforementioned effects altogether faintly, some clearly, some strongly, just as others completely. Therefore it is not sufficient to know that this drug heats or cools, but one must also determine to what extent it heats and cools. For all r...

| Metric | Score |
|--------|-------|
| BLEU-4 | 0.2477 |
| chrF++ | 0.5236 |
| METEOR | 0.4477 |
| ROUGE-L | 0.4992 |
| BERTScore | 0.9115 |
| COMET | 0.7933 |

**GEMINI**

> Concerning the faculty of simple drugs, it has been stated in another treatise that one must know the faculty of each, not only according to genus, as some have written—stating that they either heat or cool or dry or moisten—but rather distinctly and articulately, according to the order to which it belongs, as we have demonstrated. For some drugs produce each of the aforementioned effects quite faintly, others clearly, others strongly, just as still others do so completely. Therefore, it is not sufficient to know that a given drug heats or cools, but one must also determine to what degree it h...

| Metric | Score |
|--------|-------|
| BLEU-4 | 0.1996 |
| chrF++ | 0.5201 |
| METEOR | 0.4102 |
| ROUGE-L | 0.4669 |
| BERTScore | 0.9100 |
| COMET | 0.8014 |

**OPENAI**

> Concerning the power of simple drugs, it has been said in another treatise that one must know the power of each, not merely by genus, as some have written—saying that it heats or cools or dries or moistens—but in a determinate and articulated way, of what degree it is, as we have shown. For certain drugs effect each of the aforesaid actions quite faintly, others clearly, others strongly, and others completely. It is therefore not sufficient to know that this drug heats or cools; one must also specify up to what degree it heats and cools. For all resins heat, and this is common to them; yet the...

| Metric | Score |
|--------|-------|
| BLEU-4 | 0.1928 |
| chrF++ | 0.4870 |
| METEOR | 0.3927 |
| ROUGE-L | 0.4437 |
| BERTScore | 0.9055 |
| COMET | 0.7796 |

---

### Chunk 2

#### Source (Greek)

> ἀλλ’ οὐκ ἄν τις αὐτὸν ἴσως ἐν τούτῳ μέμψαιτο τοῖς ἤδη γεγυμνασμένοις κατὰ τὴν ἰατρικὴν τέχνην, οὐκ ἰδιώταις γράφοντα. τὸ δὲ μὴ προστιθέναι τὰς ἐπαγγελίας ἢ τὰς καθόλου δυνάμεις οὐ σμικρὸν ἁμάρτημα. τί γὰρ καὶ φήσει τις ἀπολογούμενος ὑπὲρ αὐτοῦ; τάχ’ ἴσως ὅτι τοῖς ἐπισταμένοις τὰς τῶν ἁπλῶν φαρμάκων δυνάμεις γέγραπται ταῦτα. καὶ μὴν οὐδεὶς ἐκείνων Ἀνδρομάχου δεῖται, δυνάμενός γε καὶ αὐτὸς ὁμοίως συντιθέναι. 16. [Λευκὴ Ἥρα πρὸς τοὺς ὑδροφόβους.] Πάλιν οὖν ἐπὶ τὸν Ἥραν ἀφικόμεθα, γράφοντα μετὰ τὴν Ἀτταλικὴν ἔμπλαστρον ἑτέραν λευκὴν, αὐτοῖς ὀνόμασι τοῖσδε· λευκὴ πρὸς τοὺς λυσσοδήκτους. ποιεῖ δ’ ἀκριβῶς καὶ πρὸς τοὺς ὑδροφόβους. ῥύεται γὰρ εὐθὺς τοῦ κινδύνου ἐπιτεθεῖσα τῷ τραύματι. τοῖς μέντοι κεκρατημένοις ἄγαν καὶ καταπότιον ὅσον καρύου Ποντικοῦ ἐξ αὐτῆς ποιήσαντα διδόναι καὶ ﻿ τοῦτο ποιεῖν ἐ...

#### Reference Translations

**Reference 1:**
> However, nobody would criticise him in the same way for writing to those already trained in medical practice and not to the laymen. But omitting the therapeutic indication or the general capacities is not a minor mistake. For what will somebody say in his defense? Perhaps that these things have been written for those who know the capacities of simple drugs. And surely none of them need Andromachus, because they can indeed compound equally well on their own. 16. White plaster by Heras for people affected by hydrophobia. So we go back to Heras, who, after the Attalic plaster, wrote another white...

#### Model Translations & Scores

**CLAUDE**

> But perhaps one might not blame him in this respect, since he writes for those already trained in the medical art, not for laymen. However, the failure to add the indications or the general properties is no small error. For what indeed will someone say in defense of him? Perhaps quickly that these things have been written for those who know the properties of simple drugs. And yet none of those men has need of Andromachus, being able himself likewise to compound them. 16. [White plaster of Heras for those afraid of water.] Again, then, we come to Heras, who writes after the Attalic plaster anot...

| Metric | Score |
|--------|-------|
| BLEU-4 | 0.1938 |
| chrF++ | 0.5144 |
| METEOR | 0.4715 |
| ROUGE-L | 0.5250 |
| BERTScore | 0.9042 |
| COMET | 0.7854 |

**GEMINI**

> But perhaps one would not blame him in this matter, since he is writing for those already trained in the medical art, not for laymen. The failure, however, to add the indications or the general properties is no small error. For what will one say in his defense? Perhaps that these things have been written for those who know the properties of simple drugs. And yet, surely, no one of them has need of Andromachus, being able himself to compound in a similar way.

16. [White Heras for those suffering from hydrophobia.]
So again we come to Heras, who, after the Attalic plaster, writes of another whi...

| Metric | Score |
|--------|-------|
| BLEU-4 | 0.2636 |
| chrF++ | 0.5427 |
| METEOR | 0.5151 |
| ROUGE-L | 0.5480 |
| BERTScore | 0.9129 |
| COMET | 0.7978 |

**OPENAI**

> But perhaps one would not blame him in this, that he writes for those already trained in the medical art, not for laymen. However, not appending the indications or the general powers is no small fault. For what could one say in his defense? Perhaps that these matters are written for those who know the powers of the simple drugs. And yet none of those men has need of Andromachus, being himself able likewise to compound them.

16. White Heras for hydrophobes. We have come again, then, to Heras, who, after the Attalic plaster, writes another white one, with this title: “White, for those bitten by...

| Metric | Score |
|--------|-------|
| BLEU-4 | 0.2164 |
| chrF++ | 0.4957 |
| METEOR | 0.4638 |
| ROUGE-L | 0.4876 |
| BERTScore | 0.8955 |
| COMET | 0.7584 |

---

### Chunk 3

#### Source (Greek)

> ἀλλὰ περὶ μὲν τούτων καὶ αὖθις εἰρήσεται, περὶ δὲ τῶν ἰσχυρῶς ῥυπτόντων φαρμάκων ἐφεξῆς ἐρῶ. 5. [Περὶ τῶν ἰσχυρῶς ῥυπτόντων φαρμάκων.] Ὅτι μὲν ἐκ τοῦ γένους ἐστὶ ταῦτα τῶν προειρημένων, ὅσα τῷ μετρίως ῥύπτειν ἕλκεσι κοίλοις, καθαροῖς, ἀπεριστάτοις προσεφέρετο μηδ’ ὅλως δάκνοντα, λέλεκται πρόσθεν. ἐπιτεταμένην δὲ τὴν ῥυπτικὴν δύναμιν ἔχει τὰ τὸν πολὺν ἀφαιροῦντα ῥύπον, ὥστ’ ἔνια τῶν εἰρημένων φαρμάκων χλωρῶν ἑνὶ μόνῳ τῶν ἁπλῶς σαρκωτικῶν διαφέρει τῷ πλήθει τοῦ ἰοῦ. τινὰ δὲ καὶ τῶν ἄλλων, ὅσα ῥύπτει σφοδρῶς μίξει, καθάπερ ἴσις ὀνομαζομένη καὶ τὸ τοῦ Μαχαιρίωνος, ᾧ ἡμεῖς χρώμεθα συνήθως, ἐλαιώδει καλουμένῳ διὰ τὴν χρῆσιν. ἔνθα γὰρ ἡμῖν πρόκειται σαρκῶσαι κόλπον, ἐλαίῳ πολλῷ τήκοντες ἐγχέομεν αὐτὸ δι’ εὐθυτρήτου κέρατος, ἐν τρόπῳ κλυστῆρος ὑείᾳ κύστει συνημμένου, χρώμεθα καὶ τοῖς καλουμένοις π...

#### Reference Translations

**Reference 1:**
> But I will talk again about these things, while next I will talk about drugs that strongly cleanse. 5. About strongly cleansing drugs. It has been said earlier that the aforementioned drugs are of the kind applied to wounds that are hollow, clean, and with no complications, since they cleanse moderately and do not bite at all. Drugs that completely remove the dirt have the cleansing capacity increased so that some of the green remedies mentioned differ from the remedies that are simply enfleshing in terms of one parameter only: the quantity of the verdigris. Among others are those that strongl...

#### Model Translations & Scores

**CLAUDE**

> But concerning these matters there will be further discussion later, and I shall speak next about the strongly cleansing drugs. 5. [Concerning the strongly cleansing drugs.] That these belong to the class of the aforementioned drugs, all those which were applied to hollow, clean, uncomplicated wounds by cleansing moderately and not biting at all, has been stated previously. Those which remove much filth possess an intensified cleansing power, so that some of the aforementioned green drugs differ from one only of the simple flesh-forming drugs in the quantity of verdigris. Some also of the othe...

| Metric | Score |
|--------|-------|
| BLEU-4 | 0.1622 |
| chrF++ | 0.4879 |
| METEOR | 0.4210 |
| ROUGE-L | 0.4606 |
| BERTScore | 0.8981 |
| COMET | 0.7580 |

**GEMINI**

> But these matters will be spoken of again, and I will speak next concerning the strongly cleansing medicaments.

5. [Concerning the strongly cleansing medicaments.]

That these are of the genus of the aforementioned medicaments—those which, by cleansing moderately, were applied to hollow, clean, uncomplicated ulcers, being not at all caustic—has been said before. But those that remove much filth have an intensified cleansing power, so that some of the aforementioned fresh medicaments differ from the simply flesh-promoting ones in one thing only: in the quantity of the verdigris. And certain ot...

| Metric | Score |
|--------|-------|
| BLEU-4 | 0.1493 |
| chrF++ | 0.4834 |
| METEOR | 0.4185 |
| ROUGE-L | 0.4702 |
| BERTScore | 0.8921 |
| COMET | 0.7290 |

**OPENAI**

> But about these matters more will be said again; next I shall speak about the strongly cleansing drugs.

5. On the strongly cleansing drugs. That these belong to the same class as those previously mentioned—those employed for cleansing moderately in hollow, clean, uncomplicated ulcers, and in no way biting—has been stated above. Those that remove a great deal of foulness possess an intensified cleansing power, so that some of the aforesaid drugs, being fresh, differ from the simple sarcotics in only one respect, namely in the degree of their acridity. And some among the others as well, those t...

| Metric | Score |
|--------|-------|
| BLEU-4 | 0.1090 |
| chrF++ | 0.4629 |
| METEOR | 0.3902 |
| ROUGE-L | 0.4444 |
| BERTScore | 0.8918 |
| COMET | 0.7520 |

---

### Chunk 4

#### Source (Greek)

> μέσης δ’ ὕλης ἐν αὐτοῖς ἐστι τὰ πικρὰ ταῖς ποιότησι, τῶν μὲν πάνυ λεπτομερῶν ἀπολειπόμενα, παχυμερὲς δ’ οὐδὲν ἔχοντα. τινὰ δ’ αὐτῶν ἀποκεχώρηκε βραχὺ τῶν μέσων, τὰ μὲν ὡς ἐπὶ τὸ θερμαίνειν, τὰ δὲ ὡς ἐπὶ τὸ ψύχειν, ὧν ἁπάντων τὰς ὕλας ἐν τῇ περὶ τῶν ἁπλῶν φαρμάκων πραγματείᾳ διῆλθον, ὥσπερ γε καὶ τῶν ἀκροδρύων, ἐν οἷς ἐστι τὰ ἀμύγδαλα τὰ πικρὰ καὶ τὰ πιστάκια. τῆς δὲ ἀπὸ τῶν φυτῶν ὕλης οὐ μέμνημαι κατὰ τὸ παρὸν, ἀνελθεῖν γὰρ ἐπὶ τὴν ἀρχὴν βούλομαι καὶ διηγήσασθαι, πότε καὶ πῶς ἐχρησάμην ἑκάστῳ τῶν ἐπινοηθέντων. ἐκ τούτου γὰρ οἶμαι τοὺς εὐφυεῖς τῶν νέων προτραπήσεσθαι,γνῶναι τὴν ὕλην τῶν φαρμάκων αὐτόπτας αὐτῆς γενομένους οὐχ ἅπαξ ἤ δὶς, ἀλλὰ πολλάκις. ἡ γὰρ τῶν αἰσθητῶν διάγνωσις ἐκ συνεχοῦς θέας ἀκριβοῦται, καὶ τούτου μέγιστόν ἐστι τεκμήριον ἡ τῶν ἀπαραλλάκτων μὲν ἡμῖν εἶναι δοκούντων διδύ...

#### Reference Translations

**Reference 1:**
> Among the substances in the middle category of matter, in terms of quality, are the bitter ones, which depart completely from those that are fine in composition, yet they have no thickness in composition. Some of them are slightly far from the middle substances in terms of warming and cooling – I discussed the matter of them all in detail in my work on simple remedies, as I did for the substance of the fruits, among which are bitter almonds and pistachios. At present I am not mentioning the matter of plants, because I want to go back to the start and set out in detail when and how we use each ...

#### Model Translations & Scores

**CLAUDE**

> Of middle material among these are the bitter things in their qualities, falling short of the very fine-particled substances, but having nothing coarse-particled. Some of them have departed slightly from the middle substances, some tending toward heating, others toward cooling, the materials of all of which I have discussed in the treatise on simple drugs, just as also the tree-fruits, among which are the bitter almonds and pistachios. But I do not mention the material from plants at the present moment, for I wish to return to the beginning and relate when and how I used each of the things dev...

| Metric | Score |
|--------|-------|
| BLEU-4 | 0.1722 |
| chrF++ | 0.5206 |
| METEOR | 0.4392 |
| ROUGE-L | 0.4690 |
| BERTScore | 0.9097 |
| COMET | 0.7565 |

**GEMINI**

> In their qualities, the bitter substances among them are of an intermediate matter, falling short of those that are very fine-particled, yet possessing nothing thick-particled. Some of them, however, have deviated slightly from the mean, some with a tendency to heat, others with a tendency to cool. The substances of all of these I have discussed in my treatise *On Simple Drugs*, as indeed I have those of the hard-shelled fruits, among which are bitter almonds and pistachios. But of the substance derived from plants I make no mention at present, for I wish to go back to the beginning and relate...

| Metric | Score |
|--------|-------|
| BLEU-4 | 0.2320 |
| chrF++ | 0.5370 |
| METEOR | 0.4666 |
| ROUGE-L | 0.4848 |
| BERTScore | 0.9097 |
| COMET | 0.7663 |

**OPENAI**

> Among them, the bitter substances, in respect of their qualities, are of material in the mean, falling short of the very fine-particled and containing nothing coarse-particled. Some of them have deviated a little from the mean, some toward heating, others toward cooling; I have gone through the materials of all these in the treatise On Simple Drugs, as likewise those of the hard-shelled fruits, among which are bitter almonds and pistachios. As for the material derived from plants, I do not for the present make mention of it, for I wish to return to the beginning and narrate when and how I empl...

| Metric | Score |
|--------|-------|
| BLEU-4 | 0.2191 |
| chrF++ | 0.5110 |
| METEOR | 0.4272 |
| ROUGE-L | 0.4797 |
| BERTScore | 0.9076 |
| COMET | 0.7530 |

---

### Chunk 5

#### Source (Greek)

> τὸ παχυμερὲς γὰρ οὐδὲν ὀνίνησι τοὺς νευροτρώτους δεομένους φαρμάκων, ὡς εἴρηται, λεπτομερῶν. ἀναλαμβανέσθω δὲ κηρωτοειδεῖ τινι τὸ διατμηθέν τε καὶ λειωθὲν συμμετρίᾳ τὴν ἀναλογίαν ἐχούσῃ τὴν προειρημένην κατὰ τὸ εὐφόρβιον. ὅσον γὰρ ἐν ἐκείνῳ τοῦ διετοῦς εὐφορβίου, τοσοῦτον ἐν τούτοις δικτάμνου τε καὶ μήου καὶ ἀκόρου βλητέον, ὅσα τ’ ἄλλα τούτοις ὁμοίως ἐστὶ θερμὰ γευομένοις. ὅσον δ’ ἐν ἐκείνοις ἐστὶ τοῦ τριετοῦς, τοσοῦτον ἐν τούτοις ἀριστολοχίας, ἴρεώς τε καὶ δρακοντίου καὶ γεντιανῆς, ὅσα τ’ ἄλλα παραπλησίως τοῖσδε πικρά ἐστιν. 8. [Περὶ τῶν πολυτελῶν σκευασιῶν τῶν πρὸς τοὺς νευροτρώτους φαρμάκων.] Οὐκ ἄχρηστον ἂν εἴη καὶ τὰ τοιαῦτα ἐπίστασθαι φάρμακα. χρεία γὰρ αὐτῶν ποτε γίγνεται σπανιώτερον, ὥσπερ τῶν εὐτελῶν πολλάκις. ὅπου γάρ τις οὐ πλείους ἔχων πεντακοσίων μυριάδων ἀνὴρ φιλοφάρμακός τε ...

#### Reference Translations

**Reference 1:**
> A thick composition does not benefit people with nerve injuries, who, as noted, require remedies of fine composition. The drug—cut and finely pounded—must be compounded with something cerate-like in the proportion indicated above for the euphorbium resin. For one must add to these formulations the same amount of dictamus, bald money,  and yellow flag as the quantity of two-year-old euphorbium resin added to that formulation, as well as equal amounts of other drugs that are likewise warming to the taste. And whatever amount of three-year-old euphorbium resin was in those remedies, the same amou...

#### Model Translations & Scores

**CLAUDE**

> For what is coarse-particled provides no benefit to those wounded in the nerves who require, as has been said, fine-particled drugs. Let the cut and ground substance be taken up in some cerate-like preparation, having in its proportion the ratio previously mentioned in the case of euphorbium. For as much as there is of two-year-old euphorbium in that preparation, so much of dittany, poppy-juice, and sweet-flag must be added in these, and whatever other things are similarly hot to the taste. And as much as there is of three-year-old euphorbium in those preparations, so much in these of birthwor...

| Metric | Score |
|--------|-------|
| BLEU-4 | 0.1684 |
| chrF++ | 0.4896 |
| METEOR | 0.4268 |
| ROUGE-L | 0.4286 |
| BERTScore | 0.9045 |
| COMET | 0.7705 |

**GEMINI**

> For that which is of coarse particles is of no benefit to those with injured nerves, who require, as has been said, medicines of fine particles. Let the substance, once it has been cut up and ground down, be incorporated into some wax-salve-like vehicle, in a proportion that has the aforementioned ratio relative to the euphorbium. For as much of the two-year-old euphorbium as is in that formula, so much of dittany and meum and acorus must be put into this one, and of as many other things as are similarly hot to the taste. And as much of the three-year-old as is in that formula, so much of aris...

| Metric | Score |
|--------|-------|
| BLEU-4 | 0.1485 |
| chrF++ | 0.4731 |
| METEOR | 0.4142 |
| ROUGE-L | 0.4153 |
| BERTScore | 0.8997 |
| COMET | 0.7771 |

**OPENAI**

> For a coarse-grained preparation does no good at all for those with nerve-wounds, who, as has been said, require finely divided drugs. Let the substances, once cut up and pulverized, be incorporated into a cerate-like vehicle, keeping the proportion previously specified with respect to the euphorbium. For the quantity of two-year-old euphorbium in that [preparation] should be matched, in these, by an equal quantity of dittany, meon, and acorus, and of whatever other substances are similarly hot to the taste; and the quantity of three-year-old euphorbium present in those should be matched, in t...

| Metric | Score |
|--------|-------|
| BLEU-4 | 0.1689 |
| chrF++ | 0.5001 |
| METEOR | 0.4080 |
| ROUGE-L | 0.4387 |
| BERTScore | 0.9003 |
| COMET | 0.7724 |

---

### Chunk 6

#### Source (Greek)

> καὶ τὸ πάχος δὲ αὐτοῦ τοῦ δεδολωμένου συνεχὲς οὐκ ἔστιν, οὐδ’ ὁμοιομερὲς, ὥσπερ τὸ τοῦ μὴ δολωθέντος, ἀλλὰ καὶ πρὸς τῷ πυθμένι τοῦ ἀγγείου παχύτερον γίγνεται. τὸ δ’ ἐπιπολῆς λεπτότερον, ὅθεν καὶ διακινοῦσιν αὐτὸ, διδόντες τοῖς ὠνουμένοις οἱ παραποιήσαντες. ἀλλὰ κᾂν ἀληθῶς ᾖ τὸ ἔλαιον ἄνευ τῆς τοιαύτης πανουργίας αὐτοφυὲς, ὄνομα μὲν ἔχει τοῦτο δὴ τὸ παλαιὸν, ἡ δύναμις δ’ οὐκ ἐγγύς ἐστι τῷ τριετεῖ πρὸς τὸ τριακονταετὲς ἢ τῷ τετραετεῖ πρὸς τὸ πεντηκονταετές. ἐπικτᾶται μὲν γάρ τινα δῆξιν ἐν τῷ χρόνῳ τό τε ἔλαιον καὶ τὸ στέαρ, ὅταν παλαιωθῇ. ἀλλὰ αὕτη μὲν μεγίστη, μεγίστη δὲ ἡ κατὰ δύναμιν ἐξαλλαγή. διαφορικώτατα γάρ ἐστι τό τε ἔλαιον καὶ τὸ στέαρ, ὅταν παλαιωθῇ. καὶ τούτου πειραθεὶς ἐγὼ διὰ τὸ κατά τινα τύχην ἔλαιόν τε καὶ στέαρ ἔχειν παλαιότατον, τοῦ πατρὸς ἐκ πολλοῦ φυλάττοντος αὐτὰ, αὐτὸς π...

#### Reference Translations

**Reference 1:**
> The thickness of the adulterated form itself is not constant, nor homogenous like the thickness of the unadulterated one, but it increases towards the bottom of the container. It is the thinner fraction on the top, whence they remove it, that the counterfeiters take and give to the buyers. Nevertheless, in reality, even when the oil is in its natural state without such adulteration, it is called ‘old’, yet 3-year-old oil has a capacity far different from 30-year-old oil, and 4-year-old oil has a capacity far different from for 50-year-old oil. For oil and fat in time acquire some bite when the...

#### Model Translations & Scores

**CLAUDE**

> And the thickness of the adulterated substance itself is not uniform, nor homogeneous, as that of the unadulterated is, but it becomes thicker toward the bottom of the vessel. The surface layer is thinner, wherefore those who have falsified it also shake it up when giving it to purchasers. But even if the oil is truly natural without such knavery, it has indeed this name "old," but its potency is not comparable—that of three-year-old oil to thirty-year-old, or four-year-old to fifty-year-old. For both oil and fat acquire a certain pungency over time, when they have aged. But this is greatest, ...

| Metric | Score |
|--------|-------|
| BLEU-4 | 0.1376 |
| chrF++ | 0.4731 |
| METEOR | 0.4370 |
| ROUGE-L | 0.4631 |
| BERTScore | 0.9052 |
| COMET | 0.7671 |

**GEMINI**

> Moreover, the consistency of the adulterated substance itself is not uniform, nor is it homogeneous, like that of the unadulterated; rather, it becomes thicker towards the bottom of the vessel, while that on the surface is thinner, for which reason the counterfeiters shake it when they give it to the buyers. But even if the oil is truly genuine and without such chicanery, it may indeed have the name 'old', but its potency is not nearly that of a three-year-old oil compared to a thirty-year-old one, or of a four-year-old to a fifty-year-old. For both oil and fat do acquire a certain pungency ov...

| Metric | Score |
|--------|-------|
| BLEU-4 | 0.2140 |
| chrF++ | 0.5091 |
| METEOR | 0.4533 |
| ROUGE-L | 0.4791 |
| BERTScore | 0.9112 |
| COMET | 0.7868 |

**OPENAI**

> And the consistency of the adulterated oil is neither uniform nor homogeneous, as is that of the unadulterated; rather, it becomes thicker toward the bottom of the vessel, while at the surface it is thinner. Hence those who have tampered with it shake it up when handing it over to purchasers. But even if the oil be truly genuine, without such knavery, it may indeed bear the title “old,” yet its efficacy is by no means comparable—the three-year-old to the thirty-year-old, or the four-year-old to the fifty-year-old. For both oil and tallow, when they have aged, acquire with time a certain acrid ...

| Metric | Score |
|--------|-------|
| BLEU-4 | 0.0908 |
| chrF++ | 0.4503 |
| METEOR | 0.4224 |
| ROUGE-L | 0.3992 |
| BERTScore | 0.9017 |
| COMET | 0.7572 |

---

### Chunk 7

#### Source (Greek)

> ἡ δὲ ἀμπελῖτις γῆ ξηραίνει τε καὶ διαφορεῖ μηδὲν ἔχουσα δριμὺ σαφῶς. καὶ διὰ τοῦτο τοῖς κακοήθεσιν ἕλκεσιν ἐπιτήδειός ἐστιν, εἰ καὶ μόνην αὐτὴν λειώσας ἐπιπάττοις. ἡ χαλβάνη δὲ καὶ αὐτὴ τῷ πεπτική τε εἶναι καὶ μαλακτικὴ καὶ παρηγορική τε καὶ ἀνώδυνος ἐμίχθη κατὰ τὴν προκειμένην σύνθεσιν, ἔχοντος μὲν καὶ τοῦ λιβανωτοῦ τὰς αὐτὰς δυνάμεις, ἀλλὰ ἀσθενεστέρας ἢ κατὰ τὴν χαλβάνην, ἐκείνης γε κατ’ ἀμφοτέρας ἰσχυροτέρας ὑπαρχούσης. ἡ τερμινθίνη δὲ ῥητίνη καὶ αὐτὴ μετὰ τοῦ ῥυπτικοῦ τε καὶ διαφορητικοῦ πεπτικὸν ἔχει τι τῶν τοιούτων διαθέσεων. ἡ δὲ ἄσφαλτος ἴσμεν ὅτι ξηραντικῆς ἐστι δυνάμεως ἅμα θερμασίᾳ μὴ πάνυ σφοδρᾷ. τούτοις οὖν ἅπασιν ὁ συνθεὶς τὴν ἔμπλαστρον ἔμιξεν ἑλκτικῆς δυνάμεως φάρμακον τὴν πρόπολιν, ἐπειδὴ πολύχρηστον ὑπάρχειν αὐτὴν ἐβούλετο. πάντα δ’ ὅσα πολύχρηστα ποικιλωτάτας ἀναγκαῖον ...

#### Reference Translations

**Reference 1:**
> Ampelitis [i.e unidentified medicinal clay] dries and disperses with no clear sharpness. For this reason it is suitable for hard-to-heal ulcers, if you pound it finely and sprinkle it on [the ulcer] by itself. Galbanum is mixed in the aforementioned formulation because it promotes concoction, softens, soothes, and relieves pain, since frankincense has the same properties but weaker whereas galbanum has both faculties stronger. Terebinth resin, in addition to a cleansing and dispersing element, has something capable of promoting concoction of such conditions. We know that bitumen has a drying c...

#### Model Translations & Scores

**CLAUDE**

> The vine-earth both dries and disperses, having nothing clearly pungent. And for this reason it is suitable for malignant ulcers, even if you should grind it alone and sprinkle it on. Galbanum itself was also mixed into the present composition because it is digestive, softening, soothing, and pain-relieving. Frankincense too possesses the same properties, but weaker than those of galbanum, since that substance is stronger in both respects. Terebinth resin itself also has, along with its cleansing and dispersive qualities, something digestive for such conditions. We know that asphalt is of dryi...

| Metric | Score |
|--------|-------|
| BLEU-4 | 0.1876 |
| chrF++ | 0.5212 |
| METEOR | 0.4656 |
| ROUGE-L | 0.5054 |
| BERTScore | 0.9005 |
| COMET | 0.7986 |

**GEMINI**

> And the ampelitis earth both dries and disperses, having clearly nothing acrid. And for this reason it is suitable for malignant ulcers, even if one were to grind it fine and sprinkle it on by itself. Galbanum itself was also mixed into the aforementioned composition on account of its being both digestive and emollient, and soothing and anodyne, although frankincense also has the same powers, but weaker than those of galbanum, since the latter is stronger in both respects. Terebinth resin itself also, along with its cleansing and dispersive quality, has a certain digestive quality for such con...

| Metric | Score |
|--------|-------|
| BLEU-4 | 0.1393 |
| chrF++ | 0.4943 |
| METEOR | 0.4254 |
| ROUGE-L | 0.4670 |
| BERTScore | 0.8899 |
| COMET | 0.7872 |

**OPENAI**

> Ampelitis earth both dries and is discutient, clearly possessing nothing acrid; and for this reason it is suitable for ill‑conditioned ulcers, even if you grind it and dust it on by itself. Galbanum, too, was included in the foregoing composition because it is concoctive, emollient, soothing, and anodyne; frankincense also has the same powers, though weaker than in galbanum, galbanum being stronger in both respects. Terebinth resin likewise, in addition to being detergent and discutient, has some concoctive efficacy for such conditions. Bitumen, we know, has a drying power, along with a heatin...

| Metric | Score |
|--------|-------|
| BLEU-4 | 0.1762 |
| chrF++ | 0.4998 |
| METEOR | 0.3764 |
| ROUGE-L | 0.4991 |
| BERTScore | 0.8974 |
| COMET | 0.7800 |

---

### Chunk 8

#### Source (Greek)

> ἐγκάθισμα πρὸς αἱμοῤῥοΐδας τὸ Φανίου. χαλκάνθου, στυπτηρίας σχιστῆς, χαλκίτεως, μίσυος ὠμοῦ, σανδαράχης ἀνὰ δραχμὰς δ΄. λεῖα πάντα ἔχε. ἐπὶ τῆς χρήσεως οὖρον παλαιὸν ταριχηρὸν ἀνδρὸς ἑνὸς, μέτρῳ ξε. β΄. βάλε εἰς ὀστρακίνην λεκάνην, τοῦ δὲ φαρμάκου δραχ. ιβ΄. προσέγχεον τοῦ οὔρου, ὥστε ἀεὶ τοὺς δύο ξέστας τηρεῖσθαι. τούτῳ χρῶ ἐγκαθίζων ἐπὶ ἡμέρας ζ΄. ἐν ταύταις γὰρ ἐνεργεῖ. ὅταν δὲ γλοιῶδες γένηται τῇ ὑποστάθμῃ, περίχριε τὸ δακτύλιον. ξηρὸν σάρκας ἐπουλοῦν, ἄδηκτον, ὡς Ἁρπόκρας. ♃ σανδαράχης, χρυσοκόλλης, ἀρσενικοῦ τὸ ἴσον ἑκάστου καὶ πρὸς κακοήθη ποιεῖ. πρὸς νομὰς ὁ Ἀσκληπιὸς λεγόμενος. ♃ χαλκίτεως, ἀρσενικοῦ τὸ ἴσον, ἀσβέστου τὸ διπλοῦν. ἔχει δὲ καὶ σανδαράχης ἴσην πρὸς τὰ ἄλλα. πρὸς τὰ ἐν δακτυλίῳ, στυπτηρίας ὑγρᾶς ἡλίκον κάρυον, σὺν μέλιτος κυάθοις δυσὶν ἑψήσας χρῶ. ξηρὸν πρὸς νομὰς ᾧ χ...

#### Reference Translations

**Reference 1:**
> Sitz bath for haemorrhoids by Phanion. Chalkanthos [copper mineral], split alum, chalkitis [i.e. copper mineral], uncooked misy [i.e. copper mineral], realgar [i.e. arsenic sulphide mineral], 4 drachmai each, all finely pounded. For administration, [add] old salted urin of one man, in the amount of 2 sextarii. Add 12 drachmai of the remedy in a clay pot. Pour also the urin so that it always maintains the [volume of] 2 sextarii. I use it by sitting on it for 7 days, for that is the duration of the drug action. Whenever it becomes slimy in the sediment, smear it over the anus. Drying, flesh-cica...

#### Model Translations & Scores

**CLAUDE**

> A sitz-bath for hemorrhoids, that of Phanius. Of chalcanthus, split alum, chalcitis, raw misy, sandarach, 4 drachmas each. Keep all ground fine. For use: stale pickled urine of one man, 2 sextarii by measure. Put it into an earthenware basin, and 12 drachmas of the drug. Pour in the urine so as always to maintain the two sextarii. Use this as a sitz-bath for 7 days, for in these days it is effective. When it becomes viscous with sediment, smear it around the anus. Dry, cicatrizing flesh, non-biting, according to Harpocras. ♃ Of sandarach, chrysocolla, arsenic, equal amounts of each; it also wo...

| Metric | Score |
|--------|-------|
| BLEU-4 | 0.1941 |
| chrF++ | 0.4684 |
| METEOR | 0.4422 |
| ROUGE-L | 0.4648 |
| BERTScore | 0.8683 |
| COMET | 0.7403 |

**GEMINI**

> A sitz-bath for hemorrhoids, that of Phanias. Of copper vitriol, fissile alum, copper pyrites, raw misy, sandarach, 4 drachmas of each. Keep all ingredients ground fine. At the time of use, take old, preserved urine of one man, 2 xestai by measure. Put this into an earthenware basin, and of the drug, 12 drachmas. Pour on some of the urine, so that the two xestai are always maintained. Use this by sitting in it for 7 days, for it is effective in this time. And when it becomes viscous in its sediment, smear it around the anus.

A dry remedy for healing flesh, non-caustic, according to Harpocras....

| Metric | Score |
|--------|-------|
| BLEU-4 | 0.1805 |
| chrF++ | 0.4688 |
| METEOR | 0.4273 |
| ROUGE-L | 0.4421 |
| BERTScore | 0.8721 |
| COMET | 0.7474 |

**OPENAI**

> Phanias’s sitz-bath for hemorrhoids. Of chalcanthum, laminated alum, chalcitis, raw misy, and sandarach, four drachmas each. Keep all finely levigated. At the time of use, take old, preserved urine of one man, in the measure of two xestai. Put it into an earthenware basin, and of the drug twelve drachmas; pour in the urine so that the two xestai are always maintained. Use this, sitting in it, for seven days; for within these it acts. And when it becomes glairy in the sediment, smear the ring. Dry; it heals flesh; non-caustic, according to Harpocrates.

Take: sandarach, chrysocolla, arsenikon—e...

| Metric | Score |
|--------|-------|
| BLEU-4 | 0.0644 |
| chrF++ | 0.3644 |
| METEOR | 0.3104 |
| ROUGE-L | 0.3350 |
| BERTScore | 0.8530 |
| COMET | 0.7330 |

---

### Chunk 9

#### Source (Greek)

> τερμινθίνης δραχ. μη΄. ἀριστολοχίας δραχ. μη΄. πίσσης δραχμὰς ἐνενήκοντα ἓξ, κηροῦ δραχμὰς ἐνενήκοντα ἓξ, ἀμμωνιακοῦ δραχμὰς ἐνενήκοντα ἕξ. οὕτως μὲν ὁ Ἀνδρόμαχος ἔγραψεν. ἔξεστί σοι καὶ δι’ ἐλάττονος συμμετρίας αὐτὴν σκευάζειν, ἑκάστου τῶν εἰρημένων τέταρτον μόριον μιγνύντα. γενήσεται γὰρ ἡ σύνθεσις τοιάδε. ♃ λιθαργύρου δραχ. λστ΄. ἀσβέστου δὲ καὶ χαλκοῦ κεκαυμένου καὶ λιβανωτοῦ καὶ τερμινθίνης καὶ ἀριστολοχίας τὸ τρίτον ἑκάστου σταθμῷ τῆς λιθαργύρου, τουτέστι δραχ. ιβ΄. εἶτα πίσσης καὶ κηροῦ καὶ ἀμμωνιακοῦ θυμιάματος, ἑκάστου τὸ διπλάσιον τῶν εἰρημένων πέμπτων φαρμάκων, τῆς ἀριστολοχίας λέγω καὶ τερμινθίνης καὶ λιβάνου καὶ χαλκοῦ κεκαυμένου καὶ ἀσβέστου. χρὴ δὲ τὴν ἄσβεστον ἀκατάσβεστον δηλονότι καὶ πρόσφατον εἶναι, οὕτω τὸ φάρμακον καὶ πρὸς τὰ σηπεδονώδη χρήσιμον γίνεται. ἅπαντα δὲ διὰ ...

#### Reference Translations

**Reference 1:**
> Terebinth resin, 48 drachmai; aristolochia, 48 drachmai; pitch, 96 drachmai; wax, 96 drachmai; gum ammoniac, 96 drachmai. Andromachus wrote thus. You can prepare a smaller batch of the compound by mixing ¼ of each of the ingredients listed. So the recipe will become as follows: litharge, 36 drachmai; unslaked lime, burnt copper, frankincense, terebinth resin, aristolochia, 1/3 of the weight of the litharge, i.e. 12 drachmai; pitch, wax, gum ammoniac, double the amount of each of the five aforementioned drugs, i.e. aristolochia, terebinth resin, frankincense, burnt copper, unslaked lime. The un...

#### Model Translations & Scores

**CLAUDE**

> Of terebinth 48 drachmas, of birthwort 48 drachmas, of pitch ninety-six drachmas, of wax ninety-six drachmas, of ammoniacum ninety-six drachmas. Thus Andromachus wrote it. It is possible for you to prepare it also with a smaller proportion, mixing a fourth part of each of the aforementioned ingredients. For the composition will be as follows: of litharge 36 drachmas; and of quicklime and burnt copper and frankincense and terebinth and birthwort, a third of each by weight of the litharge, that is 12 drachmas. Then of pitch and wax and ammoniacum incense, double each of the aforementioned five d...

| Metric | Score |
|--------|-------|
| BLEU-4 | 0.1363 |
| chrF++ | 0.4804 |
| METEOR | 0.4294 |
| ROUGE-L | 0.4826 |
| BERTScore | 0.8962 |
| COMET | 0.7585 |

**GEMINI**

> Of terebinth resin, 48 drachmas; of birthwort, 48 drachmas; ninety-six drachmas of pitch, ninety-six drachmas of wax, ninety-six drachmas of ammoniacum. Thus, then, did Andromachus write. It is also possible for you to prepare it with a smaller proportion, by mixing a fourth part of each of the aforementioned ingredients. For the composition will be as follows: of litharge, 36 drachmas; and of lime, burnt copper, frankincense, terebinth resin, and birthwort, a third of each by weight of the litharge, that is, 12 drachmas. Then, of pitch, wax, and ammoniacum incense, for each, double the amount...

| Metric | Score |
|--------|-------|
| BLEU-4 | 0.1972 |
| chrF++ | 0.5445 |
| METEOR | 0.5294 |
| ROUGE-L | 0.5321 |
| BERTScore | 0.9031 |
| COMET | 0.7789 |

**OPENAI**

> Of terebinth resin, 48 drachmae; of aristolochia, 48 drachmae; of pitch, 96 drachmae; of wax, 96 drachmae; of ammoniacum, 96 drachmae. Thus Andromachus wrote.

You may also compound it on a lesser scale of proportion, mixing a fourth part of each of the items mentioned. For the composition will be as follows: litharge, 36 drachmae; of unslaked lime, calcined copper, frankincense, terebinth resin, and aristolochia, one third each of the weight of the litharge, that is, 12 drachmae; then of pitch, wax, and ammoniacum-incense, each twice as much as the aforesaid five drugs—I mean the aristolochia...

| Metric | Score |
|--------|-------|
| BLEU-4 | 0.1893 |
| chrF++ | 0.5492 |
| METEOR | 0.5251 |
| ROUGE-L | 0.4818 |
| BERTScore | 0.9052 |
| COMET | 0.7763 |

---

### Chunk 10

#### Source (Greek)

> ι΄. ἀριστολοχίας δραχ. ι΄. οἱ δὲ κ΄. πεπέρεως λευκοῦ δραχ. ι΄. καὶ μακροῦ δραχ. ι΄. ξυλοβαλσάμου δραχ. ι΄. καρδαμώμου δραχ. ι΄. οἰσύπου δραχ. ιε΄. ἐβίσκου ῥίζης δραχ. ι΄. ξιφίου ῥίζης δραχ. ι΄. στύρακος δραχ. ι΄. καππάρεως ῥίζης δραχ. ι΄. ἴρεως Ἰλλυρικῆς δραχ. ι΄. ἀλόης Ἰνδικῆς δραχ. ι΄. χαλβάνης δραχ. ι΄. ἰξοῦ δρυΐνου δραχ. ι΄. οἱ δὲ ιβ΄. στέατος χηνείου δραχ. η΄. ῥητίνης ξηρᾶς δραχ. ιβ΄. ὑποστάθμης ἴρεως τὸ ἱκανόν. ἄλλο Ἀμυθάωνος πρὸς θώρακος καὶ ὑποχονδρίων καὶ στομάχου ἀλγηδόνας καὶ πρὸς ἀγκύλας καὶ ἀποστήματα, καὶ σκληρίας μαλάσσει. ♃ ἀμμωνιακοῦ θυμιάματος δραχ. ν΄. κηροῦ δραχ. κ΄. βδελλίου δραχ. ν΄. ῥητίνης τερμινθίνης δραχ. κ΄. ἴρεως Ἰλλυρικῆς δραχ. ι΄. χαλβάνης δραχ. ε΄. τὸ βδέλλιον οἴνῳ διαχεῖται καὶ ἀμμωνιακὸν, εἶτα καὶ τὰ τηκτὰ καταχεῖται καὶ συλλεαίνεται, ἰρίνου προσμεμιγμένου....

#### Reference Translations

**Reference 1:**
> [ingredient] 10 [drachmai]; aristolochia, 10 drachmai, some say 20; white pepper, 10 drachmai; long pepper, 10 drachmai; balsamwood [resin], 10 drachmai; cardamom, 10 drachmai; wool grease, 15 drachmai; marsh mallow root, 10 drachmai; silphium root, 10 drachmai; styrax [i.e. s. officinalis] resin, 10 drachmai; caper-plant root, 10 drachmai; Illyrian iris, 10 drachmai; Indian aloe, 10 drachmai; galbanum, 10 drachmai; birdlime [obtained from European mistletoe that grows on oak], 10 drachmai, some say 12; goose fat, 8 drachmai; dry resin, 12 drachmai; sediment of iris [unguent], as needed. Anoth...

#### Model Translations & Scores

**CLAUDE**

> 10 drachmas. Of aristolochia 10 drachmas; but some say 20. Of white pepper 10 drachmas and of long pepper 10 drachmas. Of xylobalsam 10 drachmas. Of cardamom 10 drachmas. Of oesypum 15 drachmas. Of marshmallow root 10 drachmas. Of gladiolus root 10 drachmas. Of styrax 10 drachmas. Of caper root 10 drachmas. Of Illyrian iris 10 drachmas. Of Indian aloe 10 drachmas. Of galbanum 10 drachmas. Of oak mistletoe 10 drachmas; but some say 12. Of goose fat 8 drachmas. Of dry resin 12 drachmas. Of iris sediment a sufficient amount. Another preparation of Amythaon for pains of the chest and hypochondria ...

| Metric | Score |
|--------|-------|
| BLEU-4 | 0.0664 |
| chrF++ | 0.4583 |
| METEOR | 0.3131 |
| ROUGE-L | 0.4810 |
| BERTScore | 0.8670 |
| COMET | 0.7248 |

**GEMINI**

> 10. Of aristolochia, 10 drachmas (some say 20); of white pepper, 10 drachmas; and of long pepper, 10 drachmas; of xylobalsamum, 10 drachmas; of cardamom, 10 drachmas; of oisypum, 15 drachmas; of ebiscus root, 10 drachmas; of xiphion root, 10 drachmas; of styrax, 10 drachmas; of caper root, 10 drachmas; of Illyrian iris, 10 drachmas; of Indian aloe, 10 drachmas; of galbanum, 10 drachmas; of oak mistletoe, 10 drachmas (some say 12); of goose fat, 8 drachmas; of dry resin, 12 drachmas; of iris sediment, a sufficient amount.

Another, of Amythaon, for pains of the chest, hypochondria, and stomach,...

| Metric | Score |
|--------|-------|
| BLEU-4 | 0.1761 |
| chrF++ | 0.5481 |
| METEOR | 0.3821 |
| ROUGE-L | 0.4777 |
| BERTScore | 0.8871 |
| COMET | 0.7564 |

**OPENAI**

> Aristolochia, 10 drachmas; others give 20. White pepper, 10 drachmas; and long pepper, 10. Xylobalsamum, 10. Cardamom, 10. Oesypum (wool-grease), 15. Hibiscus root, 10. Xiphion root, 10. Storax, 10. Caper root, 10. Illyrian iris, 10. Indian aloes, 10. Galbanum, 10. Oak mistletoe, 10; others, 12. Goose fat, 8. Dry resin, 12. Hypostathmē of iris, as much as suffices.

Another, by Amythaon, for pains of the chest, the hypochondria, and the stomach; also for contractures and abscesses, and it softens indurations. Gum ammoniac, 50 drachmas. Wax, 20. Bdellium, 50. Terebinth resin, 20. Illyrian iris,...

| Metric | Score |
|--------|-------|
| BLEU-4 | 0.1418 |
| chrF++ | 0.4195 |
| METEOR | 0.2919 |
| ROUGE-L | 0.5657 |
| BERTScore | 0.8502 |
| COMET | 0.6459 |

---
