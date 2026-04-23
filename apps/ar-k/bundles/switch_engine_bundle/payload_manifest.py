"""Payload manifest for the homologated switch bundle."""

from __future__ import annotations

BUNDLE_NAME = "ark_switch_engine_bundle"
PAYLOAD_VERSION = "2026.04.12-stabilized-moved-root"
PAYLOAD_ENTRIES = [
  {
    "relative_path": "FINAL_REPORT.md",
    "sha256": "b0e8356415d692475500913a0de886a1b19e03428302cd7f341cb59b0b2d2095",
    "size": 648
  },
  {
    "relative_path": "__init__.py",
    "sha256": "c6991301f3c8916b75fb28185b6824746d4206de702800851ac2380cfa353fa4",
    "size": 142
  },
  {
    "relative_path": "compat/__init__.py",
    "sha256": "57004af16829bba8c4893c95fd09a8a91079cb3b4ddeb60a7720c6d8b1f9b334",
    "size": 100
  },
  {
    "relative_path": "compat/canonical_index_shim.py",
    "sha256": "9be7dffc617e4917131025b7e1d68a584b6104ae4f8a0b355f3c85c3171afca9",
    "size": 790
  },
  {
    "relative_path": "contracts/artifact_contracts.py",
    "sha256": "6976ebf742ec398843ace0a41fa611575d3738988a594bc27e65dc44ee58bc89",
    "size": 1648
  },
  {
    "relative_path": "contracts/exclusion_policy.py",
    "sha256": "26a8e36f5a61d1d2927d55196a67a1951183ee8415cce1f28d04c43c0ba253b2",
    "size": 1738
  },
  {
    "relative_path": "contracts/homologation.py",
    "sha256": "eb7a2d51dbce21b52d75f3be54b189ba8aa460091ae089ed1c6a7896e53d70eb",
    "size": 968
  },
  {
    "relative_path": "contracts/shared_canon.py",
    "sha256": "88e524362bd44224b5c1e9ed02163c47c8b53c148e3ccfb0043102681fbc795c",
    "size": 3339
  },
  {
    "relative_path": "contracts/stage_order.py",
    "sha256": "995b1d8b4c2541e787ef28fbefca4e0edcca91e973024b570c11144883030c13",
    "size": 819
  },
  {
    "relative_path": "contracts/write_limits.py",
    "sha256": "1b26b7bcd5ada5a71dc04113fe3c3399717ebdd04ada8375471240bbfb788498",
    "size": 522
  },
  {
    "relative_path": "fixtures/__init__.py",
    "sha256": "6b6c13549c3f0475b1ff332732f0706f66cf2cfcef6390854c6010f3ddc30314",
    "size": 90
  },
  {
    "relative_path": "fixtures/catalog.py",
    "sha256": "6cef0d13f41d2e56433c9e79f1b6143a84cd1d8571ad3c6f99de804718af6a16",
    "size": 6502
  },
  {
    "relative_path": "fixtures/generated/__init__.py",
    "sha256": "bdb712c3d35925054044d134e931e21d1ebd4d49b014d11641dc75c9a7d00864",
    "size": 103
  },
  {
    "relative_path": "fixtures/generated/case_pack_001.py",
    "sha256": "c2adbb83c5ff8eefdacec7a84a83e4cc8ca768f8f508689c9577719448e307f5",
    "size": 18733
  },
  {
    "relative_path": "fixtures/generated/case_pack_002.py",
    "sha256": "53ae3bc69e8f9b03e3212372891a2e940fad78b605201356c84bd53f0ffa8d27",
    "size": 18732
  },
  {
    "relative_path": "fixtures/generated/case_pack_003.py",
    "sha256": "26aeed96e19d567784e7cd7f2803bb091661df81bc2bcfcc4889498add3d2ee5",
    "size": 18733
  },
  {
    "relative_path": "fixtures/generated/case_pack_004.py",
    "sha256": "f6e6f0f8a0235655d9006afdbfdbec24caff008714edad6f78eab1c31c4a64a0",
    "size": 18732
  },
  {
    "relative_path": "fixtures/generated/case_pack_005.py",
    "sha256": "43c1e881904be85d4ff7f672d185ffbcfe81d76533b2cfa4b0b51862a2f376e5",
    "size": 18733
  },
  {
    "relative_path": "fixtures/generated/case_pack_006.py",
    "sha256": "cb1b69feeddf01e66365cd513766aeb68dbf7d19429ee06f58c015e389578c2f",
    "size": 18732
  },
  {
    "relative_path": "fixtures/generated/case_pack_007.py",
    "sha256": "f4f2196a6aa6a541907d0d8cdfa3fa218c5afdc7464a48a7799049e260458148",
    "size": 18733
  },
  {
    "relative_path": "fixtures/generated/case_pack_008.py",
    "sha256": "3012620b742f5de40144a373d837d75b774e8c888c37e92581f1e14d5ba5b752",
    "size": 18732
  },
  {
    "relative_path": "fixtures/generated/case_pack_009.py",
    "sha256": "ac9a46e3a7bb3dbc998e411f5afcc434f905c8384779ce34f2271562dc2899a4",
    "size": 18733
  },
  {
    "relative_path": "fixtures/generated/case_pack_010.py",
    "sha256": "6e9c9c33785e8e6963c027965e30ba487f88df89bc2f81df65755a691d94bbbb",
    "size": 18732
  },
  {
    "relative_path": "fixtures/generated/case_pack_011.py",
    "sha256": "e22eff57b0f00d43619f887b0f68ad455afa5ae891306b3b8847ad6e4682b613",
    "size": 18733
  },
  {
    "relative_path": "fixtures/generated/case_pack_012.py",
    "sha256": "7e062b19699b1a5a93dd79842c7ae11cc4f2c47d043ab5bdcc3977773e78d950",
    "size": 18732
  },
  {
    "relative_path": "fixtures/generated/case_pack_013.py",
    "sha256": "ae4e95239d6cf47df15dce3b0845e57607e50f24421a594b03f4b254ad583d17",
    "size": 18733
  },
  {
    "relative_path": "fixtures/generated/case_pack_014.py",
    "sha256": "5799cb52c2916a00f11ba22f65652fa1cbd5d47969aa4d0224c67e6f53e814fa",
    "size": 18732
  },
  {
    "relative_path": "fixtures/generated/case_pack_015.py",
    "sha256": "3c2c1a7bf331cf00fe66270386f3735999062cdcaba02c210eb462a1bcc69b09",
    "size": 18733
  },
  {
    "relative_path": "fixtures/generated/case_pack_016.py",
    "sha256": "ece37e3effc2ce205d59395b9f6a9477ad6191eb8f7581d4d7cefed9c0ad3e65",
    "size": 18732
  },
  {
    "relative_path": "fixtures/generated/case_pack_017.py",
    "sha256": "2ba7232301b3d548a2d6344133cb798149f02a3581abc9cbeb1777a06b5eedef",
    "size": 18733
  },
  {
    "relative_path": "fixtures/generated/case_pack_018.py",
    "sha256": "78a4598c15bbc99db257a0d253a88cd9375de0295a593c88cabb61e1c1e02c70",
    "size": 18732
  },
  {
    "relative_path": "fixtures/generated/case_pack_019.py",
    "sha256": "82045d759053b4a38c3da083d4f6d954d7edd82d9615fd56cb3398ebc3a04241",
    "size": 18733
  },
  {
    "relative_path": "fixtures/generated/case_pack_020.py",
    "sha256": "769acc09ba077fe5f6746c753ade3572b6cb4105b2636d3c2ee5ae3fb6c5d7b2",
    "size": 18732
  },
  {
    "relative_path": "fixtures/generated/case_pack_021.py",
    "sha256": "0f97bbdb28ebafeaa1c2a18932d73d27d6a03850b7ea77943e33d58bf1f2e174",
    "size": 18733
  },
  {
    "relative_path": "fixtures/generated/case_pack_022.py",
    "sha256": "31431b30fe4b8c28ecd22ba86ddd507d26cc25d7355d900a48f10a4548a1e8e4",
    "size": 18732
  },
  {
    "relative_path": "fixtures/generated/case_pack_023.py",
    "sha256": "180ee15a75c85f39ad5eaa4e0623f291f1fb13c1dc3fc412a6aad31af1a8fe39",
    "size": 18733
  },
  {
    "relative_path": "fixtures/generated/case_pack_024.py",
    "sha256": "98ed42076f515410a736946e46db332ae3f70b138ec621af3f8f8a9d44ca91e8",
    "size": 18732
  },
  {
    "relative_path": "fixtures/generated/case_pack_025.py",
    "sha256": "f8d4cdc59f0dd71cb865538d53af2ea0595e7baa015f8b541129de8718c0cc69",
    "size": 18733
  },
  {
    "relative_path": "fixtures/generated/case_pack_026.py",
    "sha256": "4a4f4908d1c1e23a6264ac12c068e2a204ab5b51e618196949cbea4089e16e19",
    "size": 18732
  },
  {
    "relative_path": "fixtures/generated/case_pack_027.py",
    "sha256": "f7487ebccaf167dc0eb8f00d35c6add0ba26f1d0c437d55317be4a73747e18fb",
    "size": 18733
  },
  {
    "relative_path": "fixtures/generated/case_pack_028.py",
    "sha256": "63b1a9601549c20262c94525fbc4229afdc2e03dd9f83c7480e32c9ddae4452e",
    "size": 18732
  },
  {
    "relative_path": "fixtures/generated/case_pack_029.py",
    "sha256": "e29271cc4d4f320c313543f1314349a669f9e3c7e89d31a71324628531c1cf50",
    "size": 18733
  },
  {
    "relative_path": "fixtures/generated/case_pack_030.py",
    "sha256": "64793cddc83a26a4473ac0ecf69bd3c72bdd6a4a1d160c61479f0fc0dd902d79",
    "size": 18732
  },
  {
    "relative_path": "fixtures/generated/case_pack_031.py",
    "sha256": "ee1974056b4e4b5ba3dc3a96b69213ad639f148d359cc8bf706692deff5a77c2",
    "size": 18733
  },
  {
    "relative_path": "fixtures/generated/case_pack_032.py",
    "sha256": "036f95ac39e52a44f016569d6f8f1aa0cd07705fa5c05e94d63df80b524be8fa",
    "size": 18732
  },
  {
    "relative_path": "fixtures/generated/case_pack_033.py",
    "sha256": "f37194942c4f016aa6f12647c77b90e3d99fba1f78ace457ac3a454c61566f2c",
    "size": 18733
  },
  {
    "relative_path": "fixtures/generated/case_pack_034.py",
    "sha256": "47bc9b6be3840e6494b19c11ea207fd225d2b4ef26c218fd149fe0a5c8c2bf90",
    "size": 18732
  },
  {
    "relative_path": "fixtures/generated/case_pack_035.py",
    "sha256": "265a2c1dc16c7f187d4f0bff2347259ff082c49a44cbf384ce60a388c19a33e5",
    "size": 18733
  },
  {
    "relative_path": "fixtures/generated/case_pack_036.py",
    "sha256": "94ed7ea196563549abe3b5d17dae638c0894aba280c2d6fe234824ad3a4b236b",
    "size": 18732
  },
  {
    "relative_path": "fixtures/generated/case_pack_037.py",
    "sha256": "153371e6a44c3e1f581de2fa8370566794ac8c816cdac7503172fc6c8562e040",
    "size": 18733
  },
  {
    "relative_path": "fixtures/generated/case_pack_038.py",
    "sha256": "060cc87656669c78974acc4efbaf378b501f96d4d897705bc1c91b825fb9d9e5",
    "size": 18732
  },
  {
    "relative_path": "fixtures/generated/case_pack_039.py",
    "sha256": "d3495c3f96675bb1f9beb0007d277cec641bd5f2958ce0a3ec2c4687f2b823e5",
    "size": 18733
  },
  {
    "relative_path": "fixtures/generated/case_pack_040.py",
    "sha256": "b9ef3cf47eb8c11ea3f94a93b2bb627ac1b7e284a8f69af7be00b6de38187fad",
    "size": 18732
  },
  {
    "relative_path": "fixtures/generated/case_pack_041.py",
    "sha256": "97815b828327f58934af8f92160044f9ebd3788acfa1643f039fdea1c9b2619a",
    "size": 18733
  },
  {
    "relative_path": "fixtures/generated/case_pack_042.py",
    "sha256": "bf7faa219d137ef0bd6e8861ad82594a5f8bb2c485dafc4021dfefe0d883e3e9",
    "size": 18732
  },
  {
    "relative_path": "fixtures/generated/case_pack_043.py",
    "sha256": "94b549867d81e3f619826c640b10d65c367af9c963b2b8f682594d38087ec272",
    "size": 18733
  },
  {
    "relative_path": "fixtures/generated/case_pack_044.py",
    "sha256": "2782170817f085ea89248e74daa8e74c047e7120fe0ef38131ec7f8e31892ff4",
    "size": 18732
  },
  {
    "relative_path": "fixtures/generated/case_pack_045.py",
    "sha256": "50f5880cbf75c97ece89a51bbe4039b0b4ac91f63a4dcc14528b07b82d0fccb6",
    "size": 18733
  },
  {
    "relative_path": "fixtures/generated/case_pack_046.py",
    "sha256": "fd4f709412a56f28fcd1056a3484463fcaf9523d77daa933cee0e721cd50ba31",
    "size": 18732
  },
  {
    "relative_path": "fixtures/generated/case_pack_047.py",
    "sha256": "49189aacf58451ecf378f63a65fb8462f57e6e088c3a890cc33140f7f843b3ab",
    "size": 18733
  },
  {
    "relative_path": "fixtures/generated/case_pack_048.py",
    "sha256": "660d839ac8873d6a15a92d5df1b970baca241a627e9eff6700b73ff827eb12f1",
    "size": 18732
  },
  {
    "relative_path": "fixtures/generated/case_pack_049.py",
    "sha256": "f7dd8333640fe731843f7de3dbb2bd270a20cf8d64be20e285c9b12478713f91",
    "size": 18733
  },
  {
    "relative_path": "fixtures/generated/case_pack_050.py",
    "sha256": "f8e8b23d915d736a947eb9f00852b5d69cc6a7f2f77bbc884ce5b08bb7f4df4f",
    "size": 18732
  },
  {
    "relative_path": "fixtures/generated/case_pack_051.py",
    "sha256": "1c3a8eccdacb9823a3169dd4adeb5525715f5d5d5c19e645f45e08ac68b8c3cb",
    "size": 18733
  },
  {
    "relative_path": "fixtures/generated/case_pack_052.py",
    "sha256": "4e9981404720881b43762e9056696f28827c20a17326713f69accdcfccebce14",
    "size": 18732
  },
  {
    "relative_path": "fixtures/generated/case_pack_053.py",
    "sha256": "85b7be5d741a2358db72abe7a138a3055ac3d8595c75c4700fa73ca341a41017",
    "size": 18733
  },
  {
    "relative_path": "fixtures/generated/case_pack_054.py",
    "sha256": "165b6baaf53c2051cdc86b4c8ca21d3a7ba593260afba398d3f0e932048ce0f8",
    "size": 18732
  },
  {
    "relative_path": "fixtures/generated/case_pack_055.py",
    "sha256": "988fd85d752246d4c6197306b4657c995061b0b717f69e74f44373bf9e567458",
    "size": 18733
  },
  {
    "relative_path": "fixtures/generated/case_pack_056.py",
    "sha256": "5c3d06550f8af20be8d2cac412b049e0d872700ad18457fbda7020afe7c60f29",
    "size": 18732
  },
  {
    "relative_path": "fixtures/generated/case_pack_057.py",
    "sha256": "4be910dd788e9c8249ba7ff2a18ceaf97e51c79c9d89992323ce7c864f41aeec",
    "size": 18733
  },
  {
    "relative_path": "fixtures/generated/case_pack_058.py",
    "sha256": "2600bacd4b18a0eece7f2380ee21bce887b932338baf1f3cea317fd4a881e6ea",
    "size": 18732
  },
  {
    "relative_path": "fixtures/generated/case_pack_059.py",
    "sha256": "aa9cf2de979a8d2b4fa302e69516cf0d071d4773a3f0e0715a23128ddd84845c",
    "size": 18733
  },
  {
    "relative_path": "fixtures/generated/case_pack_060.py",
    "sha256": "e0068567caa07077961195852bcab09479e41822fd3c54c818dd7d619b415157",
    "size": 18732
  },
  {
    "relative_path": "fixtures/generated/case_pack_061.py",
    "sha256": "0f55eafd8fda46bfdb48db2bfb9a6e6699cb707e7822d230d77de5d1b7b30a9d",
    "size": 18733
  },
  {
    "relative_path": "fixtures/generated/case_pack_062.py",
    "sha256": "5eaa3706acc8e8555fa752b22e0d5b6dff65193a4a8c06daa51117e8a3b43564",
    "size": 18732
  },
  {
    "relative_path": "fixtures/generated/case_pack_063.py",
    "sha256": "fcbe276a962f9f65fb942540db50ce6bce72fcd612e9958f76d3d6993e0bc1d7",
    "size": 18733
  },
  {
    "relative_path": "fixtures/generated/case_pack_064.py",
    "sha256": "b30156e73fc6d7b76603301ca26e2b53eaca0e4c7fc581022fc958f1dc2e61d7",
    "size": 18732
  },
  {
    "relative_path": "fixtures/generated/case_pack_065.py",
    "sha256": "0b9d6aebeab9087806ebc16a3f3eb9f8e31faa70bd8cd8ed826f482188525562",
    "size": 18733
  },
  {
    "relative_path": "fixtures/generated/case_pack_066.py",
    "sha256": "b6b4f30769d19f9bfd29d9a6fbe3f2e56d63edb480ae2d4647b6135a30eaf2b9",
    "size": 18732
  },
  {
    "relative_path": "fixtures/generated/case_pack_067.py",
    "sha256": "fd45330616385f2a649fce6bd86c521f5c46b494dcee9660be6f2cd6f6434471",
    "size": 18733
  },
  {
    "relative_path": "fixtures/generated/case_pack_068.py",
    "sha256": "1abce274a282e1779c18cfcbb36914d009a5833e12feb5721b0d050dd60b4e74",
    "size": 18732
  },
  {
    "relative_path": "fixtures/generated/case_pack_069.py",
    "sha256": "b287a2d0943390560d716666176c0993462464f1cc1e294c0ca71c72d5f36b05",
    "size": 18733
  },
  {
    "relative_path": "fixtures/generated/case_pack_070.py",
    "sha256": "f96b73e56a101bbb059f555c1bddfa64a663505cdba090288f4f8d9186da435e",
    "size": 18732
  },
  {
    "relative_path": "fixtures/generated/case_pack_071.py",
    "sha256": "7e6827140a362c4b705f71b13f6576dd638999e93babf32c5eecc4259e4fe777",
    "size": 18733
  },
  {
    "relative_path": "fixtures/generated/case_pack_072.py",
    "sha256": "5a2dc74817b5b9dba81a2a03703fc0e38555114ae5ca43066b78fdd224426178",
    "size": 18732
  },
  {
    "relative_path": "fixtures/generated/case_pack_073.py",
    "sha256": "8853227d29a85a0af50a9f62383f5c3fa0574d36ea51abcf2a393c8c284b5890",
    "size": 18733
  },
  {
    "relative_path": "fixtures/generated/case_pack_074.py",
    "sha256": "c0dfee804ba265eb3792168e3bcbabff60b799c1d1f11c0c99623f59fb902b29",
    "size": 18732
  },
  {
    "relative_path": "fixtures/generated/case_pack_075.py",
    "sha256": "7078049484816d87b69df3a44c4cd82cc58b2adc8a62d73d5bb950e733e30f8b",
    "size": 18733
  },
  {
    "relative_path": "fixtures/generated/case_pack_076.py",
    "sha256": "80d40271c4e2a33479c95d5bbae56f2fd405a567d37d8f9dec9ce4f38fb8ce64",
    "size": 18732
  },
  {
    "relative_path": "fixtures/generated/case_pack_077.py",
    "sha256": "189e93d2e896b20e1d2f12cbe9cc698786f4707299e47c4fb3470e1f41e8f8a3",
    "size": 18733
  },
  {
    "relative_path": "fixtures/generated/case_pack_078.py",
    "sha256": "321efba935d4269b09ec01e3d907d59f6c67ba3d6281180a895c92df77ecb466",
    "size": 18732
  },
  {
    "relative_path": "fixtures/generated/case_pack_079.py",
    "sha256": "8d053c21302dba37d7e326aadf5ba9b1915ef5cf09aa21d6b5cafe20aa541b7e",
    "size": 18733
  },
  {
    "relative_path": "fixtures/generated/case_pack_080.py",
    "sha256": "7530446503e5649fdcc48de41ffe21c4ec0ba172f8e0b4ec83d8d69136418d86",
    "size": 18732
  },
  {
    "relative_path": "fixtures/generated/case_pack_081.py",
    "sha256": "830513ca12c8214bfe30d861fe5c782d674c5afe0fddd285674bdf35c28a4934",
    "size": 18733
  },
  {
    "relative_path": "fixtures/generated/case_pack_082.py",
    "sha256": "eac3cc2fa9b4d4ef37ade441eca04c1449749b1e22d72182c2a62d91b6a17c16",
    "size": 18732
  },
  {
    "relative_path": "fixtures/generated/case_pack_083.py",
    "sha256": "25b71f658386ff51d2d9883824b749bac9eb4cd3e8a3d71f1e8187daa209d117",
    "size": 18733
  },
  {
    "relative_path": "fixtures/generated/case_pack_084.py",
    "sha256": "893d7b8a82cd77072d487f1d0822903ce9c49add6969b4a614197ccef8881bac",
    "size": 18732
  },
  {
    "relative_path": "fixtures/generated/case_pack_085.py",
    "sha256": "f73c303cadb827b20da0f208f548f42b8e849e7dd2e6f75a95a1c99f9a3bb445",
    "size": 18733
  },
  {
    "relative_path": "fixtures/generated/case_pack_086.py",
    "sha256": "f0a87602ea3b9322247e5c0ce03917c6eb5235cdb3c02858ffa1a81e0699fd30",
    "size": 18732
  },
  {
    "relative_path": "fixtures/generated/case_pack_087.py",
    "sha256": "3336d219869396a5f284b2772cea3f286d7e165a8065d78162d99c25a74dfb4d",
    "size": 18733
  },
  {
    "relative_path": "fixtures/generated/case_pack_088.py",
    "sha256": "23b6fda4d8eeacddd39a9bbbb4c4fff076e792cf813b0229c56213df71597436",
    "size": 18732
  },
  {
    "relative_path": "fixtures/generated/case_pack_089.py",
    "sha256": "1708da80a660ab421602246b40a18d5bb257ffda36690b744241ce89d72afa0f",
    "size": 18733
  },
  {
    "relative_path": "fixtures/generated/case_pack_090.py",
    "sha256": "f26d33b10875e6d88edd17025c5890e46de7d4c80657f63f912c634ca239eabf",
    "size": 18732
  },
  {
    "relative_path": "fixtures/generated/case_pack_091.py",
    "sha256": "3c412ce8fe083e76d7c2f1a6b9f996dc4b374bb526f54379a1bd612f11a1ff6f",
    "size": 18733
  },
  {
    "relative_path": "fixtures/generated/case_pack_092.py",
    "sha256": "0bce130299a099947e01f6957b00eb0eed6df4bcecfb2763ae4e28c6945d95e1",
    "size": 18732
  },
  {
    "relative_path": "fixtures/generated/case_pack_093.py",
    "sha256": "7ce8c9cba7b3125be549973a3a4a189a73d6f77f33ce0c425473911d0da58fbe",
    "size": 18733
  },
  {
    "relative_path": "fixtures/generated/case_pack_094.py",
    "sha256": "e494841d73eacd3d1ec81f180ee1274d0592dca0622fd46705c1b720868c4cab",
    "size": 18732
  },
  {
    "relative_path": "fixtures/generated/case_pack_095.py",
    "sha256": "e49092afee8e4c03a84a47c23476e0996b22589bd436c13030d3a5e8e1a5f42a",
    "size": 18733
  },
  {
    "relative_path": "fixtures/generated/case_pack_096.py",
    "sha256": "da436222a4a2899f0e466cfac9a014defbb72a448a9509f4acb003429baff729",
    "size": 18732
  },
  {
    "relative_path": "fixtures/generated/case_pack_097.py",
    "sha256": "cad97f76db4f58661cfcad49b0186db232a53b02b526a76f27c3fdd49d0ca1a6",
    "size": 18733
  },
  {
    "relative_path": "fixtures/generated/case_pack_098.py",
    "sha256": "1c39dc02c10347d9a32bb8b44cfc94e473122bad6e2f39bd242f1636cb161a49",
    "size": 18732
  },
  {
    "relative_path": "fixtures/generated/case_pack_099.py",
    "sha256": "c76a51e6c117950179c032eec459b34ef2533b726a9102d95e40323e06fe7d5f",
    "size": 18733
  },
  {
    "relative_path": "fixtures/generated/case_pack_100.py",
    "sha256": "b6bb6720463bf533ae830d30dbfe6b13ddc1182ccfa95dc3a91c7a78f8fa11b5",
    "size": 18732
  },
  {
    "relative_path": "fixtures/generated/case_pack_101.py",
    "sha256": "a59221d98f700a742921d704e39a2eb1d83d8e0c4b1fd40ad36d2bc0c27a69ab",
    "size": 18733
  },
  {
    "relative_path": "fixtures/generated/case_pack_102.py",
    "sha256": "b9138f560fc6874d4ba8a08b879a6be0befddaa7ac37762a0ebfb601f51c9b0f",
    "size": 18732
  },
  {
    "relative_path": "fixtures/generated/case_pack_103.py",
    "sha256": "9cc771d76441f72706673308fbfb5a47c78d04471eb3a424eb57bc923b4ec0db",
    "size": 18733
  },
  {
    "relative_path": "fixtures/generated/case_pack_104.py",
    "sha256": "6c708c58fd542c7a1a4c71fece73df5c36eacbf9a6ce53d4854c2c817ff8b73d",
    "size": 18732
  },
  {
    "relative_path": "fixtures/generated/case_pack_105.py",
    "sha256": "23b521d320e39b13f0ae7b9f22ed19ee32ca2fee4affd2193f26cb5f71b74b9b",
    "size": 18733
  },
  {
    "relative_path": "fixtures/generated/case_pack_106.py",
    "sha256": "a489b05149ed9ad204e7988f636f10f9ef3b668f70fb06e6d76e210b9d28a8f9",
    "size": 18732
  },
  {
    "relative_path": "fixtures/generated/case_pack_107.py",
    "sha256": "74389fb875f81c9c39644d3f438826e9959d9677e5dc4cd338b6ca86d89c9e6d",
    "size": 18733
  },
  {
    "relative_path": "fixtures/generated/case_pack_108.py",
    "sha256": "804c8fc0ce2a247035dc2a8ea894c47a9cae71f5f35c5f808c4df12e67710722",
    "size": 18732
  },
  {
    "relative_path": "fixtures/generated/case_pack_109.py",
    "sha256": "d66d5ee4930591b4290521d8da33b49f39e2302f0cd4d1278c581f54cee2cf69",
    "size": 18733
  },
  {
    "relative_path": "fixtures/generated/case_pack_110.py",
    "sha256": "a7bebffc88801d6ca2750094c7350a170c75405bbd6742324be40122b3f91e33",
    "size": 18732
  },
  {
    "relative_path": "fixtures/generated/case_pack_111.py",
    "sha256": "dae52dab011cd4ffecae8cdf4548bd70817ebdab8995da45fa2ab449fc6884ae",
    "size": 18733
  },
  {
    "relative_path": "fixtures/generated/case_pack_112.py",
    "sha256": "033f23712f948a8911ae8e0100b0f5977b41857cf49625582697f275e4140353",
    "size": 18732
  },
  {
    "relative_path": "fixtures/generated/case_pack_113.py",
    "sha256": "8f3c652e5e02d665b1c393f7e3b5656621fb0b1ecf69c4a1f197addf575c3ad7",
    "size": 18733
  },
  {
    "relative_path": "fixtures/generated/case_pack_114.py",
    "sha256": "60d00b433ce1e134cef9a8789b86742822b300392aa148c2a156f5a724675135",
    "size": 18732
  },
  {
    "relative_path": "fixtures/generated/case_pack_115.py",
    "sha256": "b2faf02dc4646aca28a5410ea608e3aca1cbb02808a3599bb44910370e3fe04f",
    "size": 18733
  },
  {
    "relative_path": "fixtures/generated/case_pack_116.py",
    "sha256": "a66b65e37d10e501dbf27d85f743e0e70bc46693060755f584c51ac815ac84da",
    "size": 18732
  },
  {
    "relative_path": "fixtures/generated/case_pack_117.py",
    "sha256": "0605f28018d20396714af4089f5d0677da1045ab0801259548e4ca3ee07a10bf",
    "size": 18733
  },
  {
    "relative_path": "fixtures/generated/case_pack_118.py",
    "sha256": "4db84807e7e1175853b06427e2ce6802964f336870b7927d31fccb2165ac62e1",
    "size": 18732
  },
  {
    "relative_path": "fixtures/generated/case_pack_119.py",
    "sha256": "46dc1aa5f99b1ca238dd23f259207fa2c6d2fea6c7b006c55b83d53f7e086fdb",
    "size": 18733
  },
  {
    "relative_path": "fixtures/generated/case_pack_120.py",
    "sha256": "01d94abd31379109364104a2178f56720ba08631cc1690a7090cc10ee23761e9",
    "size": 18732
  },
  {
    "relative_path": "fixtures/generated/case_pack_121.py",
    "sha256": "3f3101ed49ae19e272a60cb185bcfdbe126babc33f36f501405bbffca976a9a0",
    "size": 18733
  },
  {
    "relative_path": "fixtures/generated/case_pack_122.py",
    "sha256": "5f04a0bbff2f18c83f803c36543e46992a830806294e165e205caed1db573723",
    "size": 18732
  },
  {
    "relative_path": "fixtures/generated/case_pack_123.py",
    "sha256": "75cacd1d7179ced3d02228e749125c52740a29950e567b12e192249b2f6a2a56",
    "size": 18733
  },
  {
    "relative_path": "fixtures/generated/case_pack_124.py",
    "sha256": "96010f76f646f1369db943cd533626ad01bda2c128763db563a927984d9fffbc",
    "size": 18732
  },
  {
    "relative_path": "fixtures/generated/case_pack_125.py",
    "sha256": "7eff7be76ceb0f93b45893a72d941bfb3eac4c93723572de82c4f69f915ef429",
    "size": 18733
  },
  {
    "relative_path": "fixtures/generated/case_pack_126.py",
    "sha256": "e1a23133b2cc7b259e0b44a4f71628e98c89a23a0688eaa5b5e05917d4aed83a",
    "size": 18732
  },
  {
    "relative_path": "fixtures/generated/case_pack_127.py",
    "sha256": "c1f811e29eb48717fee05bf8c65dbc3b9ce4e58d3f6b0734d6e46690b39d6eef",
    "size": 18733
  },
  {
    "relative_path": "fixtures/generated/case_pack_128.py",
    "sha256": "0f6c0d616b234ec2f34db7dd3a5178371c5368f59829f7556a10cfe47ac16ffc",
    "size": 18732
  },
  {
    "relative_path": "fixtures/generated/case_pack_129.py",
    "sha256": "22b2fb201612de52808cf24dcaf3d24e31590d0fb6101b8ead6c3bebefb37abd",
    "size": 18733
  },
  {
    "relative_path": "fixtures/generated/case_pack_130.py",
    "sha256": "20c1626e73b0b76bb41eaf50bda5334c0bebcb5a3cabe0129572a2c62bb49923",
    "size": 18732
  },
  {
    "relative_path": "fixtures/generated/case_pack_131.py",
    "sha256": "9d325ddebd47f5c1752da4a34fef5921f487b6ae6164120d6ab4bd069f486379",
    "size": 18733
  },
  {
    "relative_path": "fixtures/generated/case_pack_132.py",
    "sha256": "ccdce953806513955b39425e5607bb5f1d367ae2e58e5b2e2576dcf4f316e3ec",
    "size": 18732
  },
  {
    "relative_path": "fixtures/generated/case_pack_133.py",
    "sha256": "5a64758e753128fbf9eaae9ee1e40cec511b861e62a4f6fed4adb3402ce120b1",
    "size": 18733
  },
  {
    "relative_path": "fixtures/generated/case_pack_134.py",
    "sha256": "3c67c4e610d6a1b6298fa140ad8a7cdc0f0e081ddba624c8677987e0dcb3b9c3",
    "size": 18732
  },
  {
    "relative_path": "fixtures/generated/case_pack_135.py",
    "sha256": "911b09675c0985a6161cf78f385aaa1676bd4c10dec592fa26f5189f2fa78cc7",
    "size": 18733
  },
  {
    "relative_path": "fixtures/generated/case_pack_136.py",
    "sha256": "eb0b992267bd68024a3132d0603c1a731e83afc538c7d27da716a91c4fc0ee1a",
    "size": 18732
  },
  {
    "relative_path": "fixtures/generated/case_pack_137.py",
    "sha256": "a4c0362debf330fbd7474f7c2f20779b5f17ce7ee6c1b3ed41e1c5f1f7670a23",
    "size": 18733
  },
  {
    "relative_path": "fixtures/generated/case_pack_138.py",
    "sha256": "7c58d1625fdfd0cd506924b48a4ef03d871186916834718985cddd5d6dea5b8f",
    "size": 18732
  },
  {
    "relative_path": "fixtures/generated/case_pack_139.py",
    "sha256": "f6936c0af7e87aab9480debf8ef0a466dfcc76ff7245a40192d4c98ab61c7497",
    "size": 18733
  },
  {
    "relative_path": "fixtures/generated/case_pack_140.py",
    "sha256": "d5983422ef19b5d2cdd90fff154bc7b8cb37b994f927154b4746157805aeb8ed",
    "size": 18732
  },
  {
    "relative_path": "fixtures/generated/case_pack_141.py",
    "sha256": "6b99ec4a04ae2559d6021d6d29e864345f62de26e0e71f8322c467b53751d46b",
    "size": 18733
  },
  {
    "relative_path": "fixtures/generated/case_pack_142.py",
    "sha256": "a82b2c541fa347aee2f7b5d2d7fd3599e880f3d6b826541535a919177e12a88e",
    "size": 18732
  },
  {
    "relative_path": "fixtures/generated/case_pack_143.py",
    "sha256": "0d405fc36f6188372e6b6884d6c440c47a240f532ee632cc7fa531c108b87266",
    "size": 18733
  },
  {
    "relative_path": "fixtures/generated/case_pack_144.py",
    "sha256": "c43bba5417b16c1ada483d7a65ed7d7c4afefecb2eea1106db5ff57534f2869f",
    "size": 18732
  },
  {
    "relative_path": "fixtures/generated/case_pack_145.py",
    "sha256": "9a029e9a7a114dc7047d72f28f1750be688f3704173de0ab8e1b631640bad747",
    "size": 18733
  },
  {
    "relative_path": "fixtures/generated/case_pack_146.py",
    "sha256": "64606b8c630e3da8f03738cd12352972c8d539e665a1ca9a123d75bba1131032",
    "size": 18732
  },
  {
    "relative_path": "fixtures/generated/case_pack_147.py",
    "sha256": "3b4c4cc90033ddbfdc7f302b11c8a71ff8a0809546037278fb1175ea6326f10e",
    "size": 18733
  },
  {
    "relative_path": "fixtures/generated/case_pack_148.py",
    "sha256": "987b1afdc6178f72cccc769636816477ba4d3b2230b8fe3fa8cca12b0765c95e",
    "size": 18732
  },
  {
    "relative_path": "fixtures/generated/case_pack_149.py",
    "sha256": "fe32fcca3468d9e88e3c0f1280cbf01520e9655059ba1affc4ebcaefdb5e6269",
    "size": 18733
  },
  {
    "relative_path": "fixtures/generated/case_pack_150.py",
    "sha256": "c3c3b41e785e98c3219f3cd9aaa2640254ac02710d3eb8e548712efb74029aab",
    "size": 18732
  },
  {
    "relative_path": "fixtures/generated/case_pack_151.py",
    "sha256": "f18d6c6309dcf6f6baaf95581485a72b2683608b571a291ccb8c8d44c33d4d3c",
    "size": 18733
  },
  {
    "relative_path": "fixtures/generated/case_pack_152.py",
    "sha256": "9eea54d46f7a96419f2475bec8debbca276a8cf9794f9fae70e4025d15592dce",
    "size": 18732
  },
  {
    "relative_path": "fixtures/generated/case_pack_153.py",
    "sha256": "2a621590afbaa4f5a8e1c7c753155cee8031b7ad75917aa61295745a333526b0",
    "size": 18733
  },
  {
    "relative_path": "fixtures/generated/case_pack_154.py",
    "sha256": "ab622b0a57356b47dcdb6f3fe732fde635ccc5f44fe4bf93a030af64054e6b9d",
    "size": 18732
  },
  {
    "relative_path": "fixtures/generated/case_pack_155.py",
    "sha256": "06466253cd49903c84f7eb1aea6b268e18d177eaf85f045ed39a019659d8b8b3",
    "size": 18733
  },
  {
    "relative_path": "fixtures/generated/case_pack_156.py",
    "sha256": "78736174478ed261c61db37a27e33caf0a9e5be424cada2014406e0c46bcf356",
    "size": 18732
  },
  {
    "relative_path": "fixtures/generated/case_pack_157.py",
    "sha256": "b78be0e4c638a1f814445628a802a23fdd73dbfa5d2bc2b6bdeeae5d9e0c678a",
    "size": 18733
  },
  {
    "relative_path": "fixtures/generated/case_pack_158.py",
    "sha256": "772150153f655343ce19f9f087418a7f1af3b1bd705241d7f08d42d056762ad6",
    "size": 18732
  },
  {
    "relative_path": "fixtures/generated/case_pack_159.py",
    "sha256": "7f191403580b0b3eef86c735ac099f9ba72a551453afd3eefeaa5254939d04c0",
    "size": 18733
  },
  {
    "relative_path": "fixtures/generated/case_pack_160.py",
    "sha256": "e55ee1a7bda390ee0b6f0d7c9d658ba19fc7ff8499500d9c9248ba8b063929e9",
    "size": 18732
  },
  {
    "relative_path": "fixtures/replays/__init__.py",
    "sha256": "94dd1619bd6a7e4610ce913a8b7d786521180afad1506e0ca103279ff95aacea",
    "size": 90
  },
  {
    "relative_path": "fixtures/replays/replay_001.py",
    "sha256": "f753479f05a40bf7e11eca90e4ad83a96136d57b343495115c8bc47d48fb3e24",
    "size": 2296
  },
  {
    "relative_path": "fixtures/replays/replay_002.py",
    "sha256": "2f1e84ffac45f5eee7663d26cc3c299ae021cde862d4a30eef915d90d48a8465",
    "size": 2289
  },
  {
    "relative_path": "fixtures/replays/replay_003.py",
    "sha256": "d4023c92be6b2916b3f9542d46f66a12d9829fde826385cce441154770802df3",
    "size": 2296
  },
  {
    "relative_path": "fixtures/replays/replay_004.py",
    "sha256": "fcbe8019456ad6275b6551bd4bfa6ed07f853249c999552a8ab7793b1b8921ae",
    "size": 2289
  },
  {
    "relative_path": "fixtures/replays/replay_005.py",
    "sha256": "e9a04150a05a70c55c7959603212311f971f9aa88ef0141ac7cd713a86972dce",
    "size": 2296
  },
  {
    "relative_path": "fixtures/replays/replay_006.py",
    "sha256": "b1d781497eb192ea7475caf92ecd5e596b9a1c45d07bd2c7b3abd969a2712690",
    "size": 2289
  },
  {
    "relative_path": "fixtures/replays/replay_007.py",
    "sha256": "72dab6e68a5029247bd5a067ebef671a60f2169d6f4b015c06273b28b107aa67",
    "size": 2296
  },
  {
    "relative_path": "fixtures/replays/replay_008.py",
    "sha256": "8ae11e6b3f7673550644067f788318caec19d12e5b1ff3cf50c93de09fa9218e",
    "size": 2289
  },
  {
    "relative_path": "fixtures/replays/replay_009.py",
    "sha256": "57215179a46a1cfcf725ede019294cda91c8249db999733f1b3e198fcd67cc4e",
    "size": 2296
  },
  {
    "relative_path": "fixtures/replays/replay_010.py",
    "sha256": "e3dcb58ffd4fef980a2947037add7bf8af28f3291e66cccc3a0b8902caf89b78",
    "size": 2289
  },
  {
    "relative_path": "fixtures/replays/replay_011.py",
    "sha256": "c62efad730175ff50e66b740ef199da39c5f545400efcb06224d275df1fa4c10",
    "size": 2296
  },
  {
    "relative_path": "fixtures/replays/replay_012.py",
    "sha256": "dc6b4c832a683e4be32596f66316ace4ff23711bfcd706fe94d8a2df253a7dca",
    "size": 2289
  },
  {
    "relative_path": "fixtures/replays/replay_013.py",
    "sha256": "88e11e9d621c671cc3163657da108f9355ccb4a9435197f7ffe0986b840beda9",
    "size": 2296
  },
  {
    "relative_path": "fixtures/replays/replay_014.py",
    "sha256": "a7c6a9db7453ffb560c0309898f4b777e6580e1dea8cb0e2faf708ab4b617982",
    "size": 2289
  },
  {
    "relative_path": "fixtures/replays/replay_015.py",
    "sha256": "53ae3c70ff66feebf5e9d1f4ac196b81e06c495815160a3bf49b7757debc0311",
    "size": 2296
  },
  {
    "relative_path": "fixtures/replays/replay_016.py",
    "sha256": "103efa09e56ad2c56d9fc9d7929f3bbfd533132ccc975294844826b8cc13b4a0",
    "size": 2289
  },
  {
    "relative_path": "fixtures/replays/replay_017.py",
    "sha256": "54e57a80c3c85a25229785574f3f2b1dcd1558e219068108f6472f78d9a42123",
    "size": 2296
  },
  {
    "relative_path": "fixtures/replays/replay_018.py",
    "sha256": "a7026b3ccbdd9b6b33382ee2d5973eec17868b4d9c531fd49e79caab850425a8",
    "size": 2289
  },
  {
    "relative_path": "fixtures/replays/replay_019.py",
    "sha256": "3a37b59540563acc08452de4be0f407cc44dc8e883c1c572426dcd360537b4cc",
    "size": 2296
  },
  {
    "relative_path": "fixtures/replays/replay_020.py",
    "sha256": "fff29fd4d963631371bff55119653371bdde572f8b55486fbad058a5253a7b30",
    "size": 2289
  },
  {
    "relative_path": "fixtures/replays/replay_021.py",
    "sha256": "a2b220c922426ab607850590dbc350498942acdba0edb747f7676b2b922c72f0",
    "size": 2296
  },
  {
    "relative_path": "fixtures/replays/replay_022.py",
    "sha256": "5ebcb96387fb185594834380904985d1a4ce8e621eb3816dc64f0477cc61b0fd",
    "size": 2289
  },
  {
    "relative_path": "fixtures/replays/replay_023.py",
    "sha256": "98d9e4f0af8b4c6832e5ebbbe70ef85b11757afc7ace7becaa8225da633d3afd",
    "size": 2296
  },
  {
    "relative_path": "fixtures/replays/replay_024.py",
    "sha256": "d612c174e6d6111e968f487c7ebc4d7619693c5e50e0c78f6a7c2ef19d09f9f9",
    "size": 2289
  },
  {
    "relative_path": "fixtures/replays/replay_025.py",
    "sha256": "cc03ff61a4aa0b66b8a6a70b56ba2ef12e3046b1c61f86439f73b8db6ccd9780",
    "size": 2296
  },
  {
    "relative_path": "fixtures/replays/replay_026.py",
    "sha256": "96f85a915ede634eb660dcfcdcd34b6d801968d748f9791dd2a1acae1e8f0590",
    "size": 2289
  },
  {
    "relative_path": "fixtures/replays/replay_027.py",
    "sha256": "99038c12f2b6cceecd038902bb1fbf4a2ec3aceaaa695edc18221c9573841748",
    "size": 2296
  },
  {
    "relative_path": "fixtures/replays/replay_028.py",
    "sha256": "aeac6d6ff9d5886c5ec630a080c0fc1bca59eec339f27066041c359e2a6bb985",
    "size": 2289
  },
  {
    "relative_path": "fixtures/replays/replay_029.py",
    "sha256": "937e9ff44ad116910203540615a49eeb0e6a4dd7d214aec85272242bdee6a07a",
    "size": 2296
  },
  {
    "relative_path": "fixtures/replays/replay_030.py",
    "sha256": "ddc8cb7e1de5ee9bf29fde62450e4d5ab7d1c5ba90f71357b6913b23b3b87e89",
    "size": 2289
  },
  {
    "relative_path": "fixtures/replays/replay_031.py",
    "sha256": "11283707a9a1967937fe70c02f9269de06bfb98aee67a588119ac4d905b6294e",
    "size": 2296
  },
  {
    "relative_path": "fixtures/replays/replay_032.py",
    "sha256": "1f688de5a7300f0475afe979bb90f8302047a079e666beb841cac47c25ea4195",
    "size": 2289
  },
  {
    "relative_path": "fixtures/replays/replay_033.py",
    "sha256": "bcb9a657a39e744a2d1cc00fe163d9f264fb7c531aa2c10bbf958f6cedd27919",
    "size": 2296
  },
  {
    "relative_path": "fixtures/replays/replay_034.py",
    "sha256": "9d77e955012db30cb78a351e78179765f5c1eb7d08edc27168ce98e175ebcc5e",
    "size": 2289
  },
  {
    "relative_path": "fixtures/replays/replay_035.py",
    "sha256": "ad545baf84095c8fbb7757533463a931a3e7c24b635b1bd796c5e13cc0d6b02a",
    "size": 2296
  },
  {
    "relative_path": "fixtures/replays/replay_036.py",
    "sha256": "11c129c6b5f5e7627dc82a1d2ae41119271c6a42d4f57f4c9691339b8dfbcb80",
    "size": 2289
  },
  {
    "relative_path": "fixtures/replays/replay_037.py",
    "sha256": "23681e06e44688a669526dc1d3493cf9a9f07ff977fe3b9d8e71ca8a68083c8e",
    "size": 2296
  },
  {
    "relative_path": "fixtures/replays/replay_038.py",
    "sha256": "d642902fda60e7c26f85d24d4484e6f82b673bc80e5e10148ed44312a8b31a8f",
    "size": 2289
  },
  {
    "relative_path": "fixtures/replays/replay_039.py",
    "sha256": "4e674457ad7b91557801debb4dc1b29f67d4bb6a231b15f7d32bfa54ff3be0c8",
    "size": 2296
  },
  {
    "relative_path": "fixtures/replays/replay_040.py",
    "sha256": "5513f9d69f3ab5f42de489c9ed60cd6ded432ac44283419d5bee051c6d1b6859",
    "size": 2289
  },
  {
    "relative_path": "payload_manifest.py",
    "sha256": "66edb808b9a813dcf96a50e8b8afc7bf3a59f87598349e326f6101e47ac65b6a",
    "size": 38657
  },
  {
    "relative_path": "switch_engine/__init__.py",
    "sha256": "7e1f03dfa2ccfd5d7461250f6cfa14dfeca314223cbdd584915409afbd7d6349",
    "size": 201
  },
  {
    "relative_path": "switch_engine/invariants.py",
    "sha256": "bfde68d7ffedfd01361a3977c9f69711943911b74d4a2d5c944ccca02b273fd0",
    "size": 1183
  },
  {
    "relative_path": "switch_engine/models.py",
    "sha256": "6f2737c173490ee933ef91935b8652ba8562910c023d8b8e24000e92ee7cdf30",
    "size": 512
  },
  {
    "relative_path": "switch_engine/registry_io.py",
    "sha256": "074035e63520a53417d7d5b922e7402093f401a0a454337ecc577901e81234a3",
    "size": 1418
  },
  {
    "relative_path": "switch_engine/resolver.py",
    "sha256": "cbbd80cdfe4a4326cb4e831da986261a7c523bc5c1e32738e3411d9b12a83b03",
    "size": 3741
  },
  {
    "relative_path": "switch_engine/tracing.py",
    "sha256": "9f2dd98ac715424fa87c8f0e546bd69f5c32a42edcc5bfbe1407aac5f71d63cb",
    "size": 806
  },
  {
    "relative_path": "switch_engine_installer.py",
    "sha256": "59cda160196bc5415bcd3e6a4c3a1f9ddedb3de5a09d59f59714633da28a0e82",
    "size": 8392
  },
  {
    "relative_path": "tests/__init__.py",
    "sha256": "a1ad7a38ce5aecf641d4541edd75e34f8f1e60d088cea4b231ed8f95048cf857",
    "size": 84
  },
  {
    "relative_path": "tests/test_bundle_tools.py",
    "sha256": "794adfc6757b4fe188bee95687a846c81dd9ba020871abf7513bdb6c6d043a3b",
    "size": 878
  },
  {
    "relative_path": "tests/test_installer_contract.py",
    "sha256": "8391603531c7bc7db598f72cb12d67139cfe1a56e030b3a01a77fa1d9e4b6883",
    "size": 3456
  },
  {
    "relative_path": "tests/test_switch_engine_core.py",
    "sha256": "85eb484d6c3ede407fce2df6655e404d22cf0fbc4f0ba11651247e3bb5b434a8",
    "size": 3486
  },
  {
    "relative_path": "tests/test_switch_output_contract.py",
    "sha256": "5ca061f485dc4d8ec6550800ae57a991db7f5c04bd3852d99374edf4f124066d",
    "size": 3126
  },
  {
    "relative_path": "tools/__init__.py",
    "sha256": "97c23727d2b8fd1521c2b527129d610621a869aa8534e1802c20019ba211951b",
    "size": 96
  },
  {
    "relative_path": "tools/count_bundle_mix.py",
    "sha256": "f6ad4dcf14987a22efa0f08c7afcbe9179112278626f971f8bba9b677d6ecb42",
    "size": 2212
  },
  {
    "relative_path": "tools/generate_example_outputs.py",
    "sha256": "a9b74bfd73b532ca017847b150482c6f25f7faf805bab7a8a77b85d4b0f2ce08",
    "size": 2067
  },
  {
    "relative_path": "tools/validate_switch_engine_bundle.py",
    "sha256": "4b0286937afae157b4aafb2cca7820689f6fe0b291dc5643f8f0515b6b022fcf",
    "size": 2913
  }
]
