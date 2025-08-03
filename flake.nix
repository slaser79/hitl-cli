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
        python = pkgs.python312;
        pythonPackages = python.pkgs;
        
        # Build the Python package
        hitl-cli-package = pythonPackages.buildPythonApplication {
          pname = "hitl-cli";
          version = "0.1.0";
          src = ./.;
          pyproject = true;
          
          nativeBuildInputs = with pythonPackages; [
            hatchling
          ];
          
          propagatedBuildInputs = with pythonPackages; [
            google-auth
            google-auth-oauthlib
            httpx
            typer
            fastmcp
            pyjwt
            authlib
            pynacl
          ];
          
          # Skip runtime dependency checks since nixpkgs versions may be slightly different
          dontCheckRuntimeDeps = true;
          
          doCheck = true;
          nativeCheckInputs = with pythonPackages; [
            pytest
            pytest-asyncio
            pytest-cov
          ];
          
          meta = with pkgs.lib; {
            description = "Command-line interface for Human-in-the-Loop services";
            license = licenses.mit;
            platforms = platforms.unix;
          };
        };
        
      in {
        packages = {
          # The main Python package
          package = hitl-cli-package;
          
          # Default package (same as package for this project)
          default = hitl-cli-package;
          
          # Development wrapper for local testing with source code
          dev-wrapper = pkgs.writeShellScriptBin "hitl-cli-dev" ''
            # Use the local source for development
            export PYTHONPATH="${./.}:$PYTHONPATH"
            
            # Use Python with all the dependencies
            exec ${python.withPackages (ps: with ps; [
              google-auth
              google-auth-oauthlib
              httpx
              typer
              fastmcp
              pyjwt
              authlib
              pynacl
            ])}/bin/python -m hitl_cli.main "$@"
          '';
        };
        
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            python312
            uv
          ];
          
          inputsFrom = [ hitl-cli-package ];
          
          shellHook = ''
            echo "HITL CLI Development Environment"
            echo "Python: $(python --version)"
            echo "uv: $(uv --version)"
            echo ""
            echo "Available build commands:"
            echo "  nix build                    - Build wrapped CLI executable"
            echo "  nix build .#package          - Build Python package"
            echo "  nix build .#dev-wrapper      - Build development wrapper"
            echo "  nix run . -- --help          - Run built CLI with arguments"
            echo ""
            
            # Create and activate virtual environment
            if [ ! -d .venv ]; then
              uv venv
            fi
            source .venv/bin/activate
            
            # Sync dependencies and install the CLI in editable mode
            uv sync
            uv pip install -e .
            
            echo "Virtual environment activated. Run 'hitl-cli --help' to get started."
          '';
        };
      });
}
