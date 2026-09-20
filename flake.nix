{
    description = "Cryptanalysis coursework: DLP algorithms, ElGamal/RSA attacks, and proofs (SageMath)";

    inputs = {
        nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
        flake-utils.url = "github:numtide/flake-utils";
    };

    outputs = { self, nixpkgs, flake-utils }:
        flake-utils.lib.eachDefaultSystem (system:
            let
                pkgs = import nixpkgs { inherit system; };
            in
                {
                devShells.default = pkgs.mkShell {
                    packages = [ pkgs.sage ];

                    shellHook = ''
                        export PYTHONPATH="$PWD:$PYTHONPATH"
                        echo "SageMath devShell ready. Run tests with 'sage -t tests/' or benchmarks with 'sage benchmarks/bench_dlp.py'."
                    '';
                };
            });
}

