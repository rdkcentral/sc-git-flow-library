import logging
from pathlib import Path
import subprocess

logger = logging.getLogger(__name__)

class GitFlowLibrary:
    @staticmethod
    def is_gitflow_enabled(directory: str | Path) -> bool:
        try:
            result = subprocess.run(
                ['git', 'config', '--get-regexp', '^gitflow'],
                cwd=directory,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True
            )
            return result.returncode == 0 and bool(result.stdout.strip())
        except Exception:
            return False

    @staticmethod
    def get_git_root(directory: str | Path) -> Path | None:
        """Returns the first .git found in directories above.
        
        Args:
            directory: The directory to search upward from. Defaults to 
                current working directory.
        """
        path = Path(directory).resolve()
        while path != path.parent:
            candidate = path / '.git'
            if candidate.is_dir():
                return candidate
            path = path.parent
        return None

    @staticmethod
    def init(directory: str | Path, defaults:bool=True):
        """Initialises a repository for git flow commands.
        
        Args:
            directory (str): Where to initialise git flow.
            defaults (bool): If true use the default branch names for git-flow, if false
                the user will be prompted. Defaults to True.
        """
        cmd = ['git', 'flow', 'init']
        if defaults:
            cmd.append('-d')

        logger.info(f"In {directory}: {cmd}")
        subprocess.run(cmd, cwd=directory, check=True)
    
    @staticmethod
    def start(
        directory: str | Path,
        branch_type: str,
        name: str,
        base: str | None = None,
        fetch: bool = False
    ):
        cmd = ['git', 'flow', branch_type, 'start']
        if fetch:
            cmd.append('-f')
        cmd.append(name)
        if base:
            cmd.append(base)

        subprocess.run(cmd, cwd=directory, check=True)
    
    @staticmethod
    def checkout(
        directory: str | Path,
        branch_type: str,
        name: str | None
    ):
        cmd = ['git', 'flow', branch_type, 'checkout']
        if name:
            cmd.append(name)
        subprocess.run(cmd, cwd=directory, check=True)

    @staticmethod
    def finish(
        directory: str | Path,
        branch_type: str,
        name: str | None = None,
        fetch: bool = False,
        keep: bool = False,
        tag_message: str | None = False
    ):
        """Finish and merge a branch.

        Args:
            directory (str | Path): Directory to run the command.
            branch_type (str): feature, release or hotfix.
            name (str | None, optional): Name of branch. Defaults to None which targets
                current branch.
            fetch (bool, optional): Fetch from remote before. Defaults to False.
            keep (bool, optional): Keep branch after finish. Defaults to False.
            tag_message (str | None, optional): Use given tag message. Defaults to False.

        Raises:
            ValueError: If tag_message used with wrong branch_type.
        """    
        cmd = ['git', 'flow', branch_type, 'finish']
        if name:
            cmd.append(name)
        if fetch:
            cmd.append('-F')
        if keep:
            cmd.append('-k')
        if tag_message:
            if branch_type in ('release', 'hotfix'):
                cmd.extend(['-m', tag_message])
            else:
                raise ValueError(
                    "tag_message is only valid for release or hotfix branches")
        subprocess.run(cmd, cwd=directory, check=True)

    @staticmethod
    def get_master_branch(directory: str | Path) -> str | None:
        branch = GitFlowLibrary.get_config_value('branch.master', directory)
        if not branch:
            raise RuntimeError(
                "Master branch not set in gitflow config. This shouldn't be possible.")
        return branch
    
    @staticmethod
    def get_develop_branch(directory: str | Path) -> str | None:
        branch = GitFlowLibrary.get_config_value('branch.develop', directory)
        if not branch:
            raise RuntimeError(
                "Develop branch not set in gitflow config. This shouldn't be possible.")
        return branch
    
    @staticmethod
    def get_branch_base(branch: str, directory: str | Path) -> str | None:
        """Get the base branch for a given gitflow branch.

        Args:
            branch (str): The branch to find the base of.
            directory (str | Path): Path to repository directory.

        Returns:
            str | None: The base branch name if set, otherwise None.
        """        
        return GitFlowLibrary.get_config_value(f'branch.{branch}.base', directory)
    
    @staticmethod
    def set_branch_base(branch: str, base: str, directory: str | Path):
        """Set the base branch for a given gitflow branch.

        Args:
            branch (str): The branch to configure.
            base (str): The base branch name to associate.
            directory (str | Path): Path to the repository directory.

        Raises:
            RuntimeError: If gitflow not enabled.
        """        
        if not GitFlowLibrary.is_gitflow_enabled(directory):
            raise RuntimeError(
                f"Tried to set gitflow branch base in {directory} but gitflow "
                "not enabled!"
            )
        subprocess.run(
            ['git', 'flow', 'config', 'base', '--set', branch, base],
            cwd=directory
        )
    
    @staticmethod
    def get_config_value(key: str, directory: str | Path) -> str | None: 
        """Get a gitflow config value for a repo in given directory.

        Args:
            key (str): The gitflow config key to retrieve (e.g. 'branch.master')
            directory (str | Path): Path to repository directory.

        Raises:
            RuntimeError: If gitflow is not enabled in the specified directory.

        Returns:
            str | None: The configuration value if set, otherwise None.
        """        
        if not GitFlowLibrary.is_gitflow_enabled(directory):
            raise RuntimeError(
                f"Tried to read gitflow config in {directory} but gitflow "
                "not enabled!"
            )
        out = subprocess.run(
            ['git', 'config', f'gitflow.{key}'],
            cwd=directory,
            capture_output=True,
            text=True
        ).stdout.strip()
        return out if out else None