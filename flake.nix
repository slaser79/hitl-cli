{
  description = "HITL CLI - Human-in-the-Loop Command Line Interface";
  
  inputs = {
    flake-utils.url = "github:numtide/flake-utils";
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
  };
  
  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
      in {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            python312
            uv
          ];
          
          shellHook = ''
            echo "HITL CLI Development Environment"
            echo "Python: $(python --version)"
            echo "uv: $(uv --version)"
            
            # Create and activate virtual environment
            if [ ! -d .venv ]; then
              uv venv
            fi
            source .venv/bin/activate
            
            # Sync dependencies
            uv sync
            
            echo ""
            echo "Virtual environment activated. Run 'hitl-cli --help' to get started."
          '';
        };
      });
}
